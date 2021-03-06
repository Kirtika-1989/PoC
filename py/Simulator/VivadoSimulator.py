# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# 
# ==============================================================================
# Authors:          Patrick Lehmann
#                   Martin Zabel
# 
# Python Class:      TODO
# 
# Description:
# ------------------------------------
#		TODO:
#		- 
#		- 
#
# License:
# ==============================================================================
# Copyright 2007-2016 Technische Universitaet Dresden - Germany
#                     Chair for VLSI-Design, Diagnostics and Architecture
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
# entry point
if __name__ != "__main__":
	# place library initialization code here
	pass
else:
	from lib.Functions import Exit
	Exit.printThisIsNoExecutableFile("The PoC-Library - Python Module Simulator.VivadoSimulator")


# load dependencies
from pathlib                    import Path

from Base.Project               import ToolChain, Tool
from Base.Simulator             import SimulatorException, Simulator as BaseSimulator, VHDL_TESTBENCH_LIBRARY_NAME, SkipableSimulatorException
from Base.Logging               import Severity
from ToolChains.Xilinx.Xilinx   import XilinxProjectExportMixIn
from ToolChains.Xilinx.Vivado   import Vivado, VivadoException


class Simulator(BaseSimulator, XilinxProjectExportMixIn):
	_TOOL_CHAIN =            ToolChain.Xilinx_Vivado
	_TOOL =                  Tool.Xilinx_xSim

	def __init__(self, host, guiMode):
		super().__init__(host)
		XilinxProjectExportMixIn.__init__(self)

		self._guiMode =        guiMode

		self._entity =        None
		self._testbenchFQN =  None
		self._vhdlVersion =    None
		self._vhdlGenerics =  None

		self._vivado =        None

		vivadoFilesDirectoryName = host.PoCConfig['CONFIG.DirectoryNames']['VivadoSimulatorFiles']
		self.Directories.Working = host.Directories.Temp / vivadoFilesDirectoryName
		self.Directories.PreCompiled = host.Directories.PreCompiled / vivadoFilesDirectoryName

		self._PrepareSimulationEnvironment()
		self._PrepareSimulator()

	def _PrepareSimulator(self):
		# create the Vivado executable factory
		self._LogVerbose("Preparing Vivado simulator.")
		vivadoSection = self.Host.PoCConfig['INSTALL.Xilinx.Vivado']
		version =  vivadoSection['Version']
		binaryPath = Path(vivadoSection['BinaryDirectory'])
		self._vivado = Vivado(self.Host.Platform, binaryPath, version, logger=self.Logger)

	def _RunElaboration(self, testbench):
		xelabLogFilePath =  self.Directories.Working / (testbench.ModuleName + ".xelab.log")
		prjFilePath =        self.Directories.Working / (testbench.ModuleName + ".prj")
		self._WriteXilinxProjectFile(prjFilePath, "xSim", self._vhdlVersion)

		# create a VivadoLinker instance
		xelab = self._vivado.GetElaborator()
		xelab.Parameters[xelab.SwitchTimeResolution] =  "1fs"	# set minimum time precision to 1 fs
		xelab.Parameters[xelab.SwitchMultiThreading] =  "off" if self.Logger.LogLevel is Severity.Debug else "auto"		# disable multithreading support in debug mode
		xelab.Parameters[xelab.FlagRangeCheck] =        True

		xelab.Parameters[xelab.SwitchOptimization] =    "0" if self.Logger.LogLevel is Severity.Debug else "2"		# set to "0" to disable optimization
		xelab.Parameters[xelab.SwitchDebug] =           "typical"
		xelab.Parameters[xelab.SwitchSnapshot] =        testbench.ModuleName

		xelab.Parameters[xelab.SwitchVerbose] =         "1" if self.Logger.LogLevel is Severity.Debug else "0"		# set to "1" for detailed messages
		xelab.Parameters[xelab.SwitchProjectFile] =     str(prjFilePath)
		xelab.Parameters[xelab.SwitchLogFile] =         str(xelabLogFilePath)
		xelab.Parameters[xelab.ArgTopLevel] =           "{0}.{1}".format(VHDL_TESTBENCH_LIBRARY_NAME, testbench.ModuleName)

		try:
			xelab.Link()
		except VivadoException as ex:
			raise SimulatorException("Error while analysing '{0!s}'.".format(prjFilePath)) from ex
		if xelab.HasErrors:
			raise SkipableSimulatorException("Error while analysing '{0!s}'.".format(prjFilePath))

	def _RunSimulation(self, testbench):
		xSimLogFilePath =    self.Directories.Working / (testbench.ModuleName + ".xSim.log")
		tclBatchFilePath =  self.Host.Directories.Root / self.Host.PoCConfig[testbench.ConfigSectionName]['xSimBatchScript']
		tclGUIFilePath =    self.Host.Directories.Root / self.Host.PoCConfig[testbench.ConfigSectionName]['xSimGUIScript']
		wcfgFilePath =      self.Host.Directories.Root / self.Host.PoCConfig[testbench.ConfigSectionName]['xSimWaveformConfigFile']

		# create a VivadoSimulator instance
		xSim = self._vivado.GetSimulator()
		xSim.Parameters[xSim.SwitchLogFile] =          str(xSimLogFilePath)

		if (not self._guiMode):
			xSim.Parameters[xSim.SwitchTclBatchFile] =  str(tclBatchFilePath)
		else:
			xSim.Parameters[xSim.SwitchTclBatchFile] =  str(tclGUIFilePath)
			xSim.Parameters[xSim.FlagGuiMode] =          True

			# if xSim save file exists, load it's settings
			if wcfgFilePath.exists():
				self._LogDebug("Found waveform config file: '{0!s}'".format(wcfgFilePath))
				xSim.Parameters[xSim.SwitchWaveformFile] =  str(wcfgFilePath)
			else:
				self._LogDebug("Didn't find waveform config file: '{0!s}'".format(wcfgFilePath))

		xSim.Parameters[xSim.SwitchSnapshot] = testbench.ModuleName
		testbench.Result = xSim.Simulate()
