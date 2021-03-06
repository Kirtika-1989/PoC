# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# 
# ==============================================================================
# Authors:          Patrick Lehmann
#                   Martin Zabel
#
# Python Module:    TODO
# 
# Description:
# ------------------------------------
#		TODO:
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

from lib.Parser           import AndExpression, OrExpression, XorExpression, NotExpression, InExpression, NotInExpression
from lib.Parser           import EqualExpression, UnequalExpression, LessThanExpression, LessThanEqualExpression, GreaterThanExpression, GreaterThanEqualExpression
from lib.Parser           import ExistsFunction, ListConstructorExpression
from lib.Parser           import ParserException
from lib.Parser           import StringLiteral, IntegerLiteral, Identifier
from Parser.FilesCodeDOM  import Document
from Parser.FilesCodeDOM  import IfElseIfElseStatement, ReportStatement
from Parser.FilesCodeDOM  import IncludeStatement, LibraryStatement
from Parser.FilesCodeDOM  import UcfStatement, XdcStatement, SdcStatement
from Parser.FilesCodeDOM  import VHDLStatement, VerilogStatement, CocotbStatement


class FileReference:
	def __init__(self, file):
		self._file =    file

	@property
	def File(self):
		return self._file

	def __repr__(self):
		return str(self._file)


class IncludeFileMixIn(FileReference):
	def __str__(self):
		return "Include file: '{0!s}'".format(self._file)


class VHDLSourceFileMixIn(FileReference):
	def __init__(self, file, library):
		super().__init__(file)
		self._library =  library

	@property
	def LibraryName(self):
		return self._library

	def __str__(self):
		return "VHDL file: {0} '{1!s}'".format(self._library, self._file)


class VerilogSourceFileMixIn(FileReference):
	def __str__(self):
		return "Verilog file: '{0!s}'".format(self._file)


class CocotbSourceFileMixIn(FileReference):
	def __str__(self):
		return "Cocotb file: '{0!s}'".format(self._file)


class UcfSourceFileMixIn(FileReference):
	def __str__(self):
		return "UCF file: '{0!s}'".format(self._file)


class XdcSourceFileMixIn(FileReference):
	def __str__(self):
		return "XDC file: '{0!s}'".format(self._file)


class SdcSourceFileMixIn(FileReference):
	def __str__(self):
		return "SDC file: '{0!s}'".format(self._file)


class VHDLLibraryReference:
	def __init__(self, name, path):
		self._name = name.lower()
		self._path = path
	
	@property
	def Name(self):
		return self._name
		
	@property
	def Path(self):
		return self._path
	
	def __str__(self):
		return "VHDL library: {0} in '{1}'".format(self._name, str(self._path))
	
	__repr__ = __str__


class FilesParserMixIn:
	_classIncludeFile =         IncludeFileMixIn
	_classVHDLSourceFile =      VHDLSourceFileMixIn
	_classVerilogSourceFile =   VerilogSourceFileMixIn
	_classCocotbSourceFile =    CocotbSourceFileMixIn
	_classUcfSourceFile =       UcfSourceFileMixIn
	_classXdcSourceFile =       XdcSourceFileMixIn
	_classSdcSourceFile =       SdcSourceFileMixIn

	def __init__(self):
		self._rootDirectory =  None
		self._document =      None
		
		self._files =          []
		self._includes =      []
		self._libraries =      []
		self._warnings =      []
		
	def _Parse(self):
		self._ReadContent() #only available via late binding
		self._document = Document.parse(self._content, printChar=not True) #self._content only available via late binding
		# print(Fore.LIGHTBLACK_EX + str(self._document) + Fore.RESET)
		
	def _Resolve(self, statements=None):
		# print("Resolving {0}".format(str(self._file)))
		if (statements is None):
			statements = self._document.Statements
		
		for stmt in statements:
			if isinstance(stmt, VHDLStatement):
				file =            self._rootDirectory / stmt.FileName
				vhdlSrcFile =     self._classVHDLSourceFile(file, stmt.LibraryName)		# stmt.Library,
				self._files.append(vhdlSrcFile)
			elif isinstance(stmt, VerilogStatement):
				file =            self._rootDirectory / stmt.FileName
				verilogSrcFile =  self._classVerilogSourceFile(file)
				self._files.append(verilogSrcFile)
			elif isinstance(stmt, CocotbStatement):
				file =            self._rootDirectory / stmt.FileName
				cocotbSrcFile =   self._classCocotbSourceFile(file)
				self._files.append(cocotbSrcFile)
			elif isinstance(stmt, UcfStatement):
				file =            self._rootDirectory / stmt.FileName
				ucfSrcFile =      self._classCocotbSourceFile(file)
				self._files.append(ucfSrcFile)
			elif isinstance(stmt, XdcStatement):
				file =            self._rootDirectory / stmt.FileName
				xdcSrcFile =      self._classCocotbSourceFile(file)
				self._files.append(xdcSrcFile)
			elif isinstance(stmt, SdcStatement):
				file =            self._rootDirectory / stmt.FileName
				sdcSrcFile =      self._classCocotbSourceFile(file)
				self._files.append(sdcSrcFile)
			elif isinstance(stmt, IncludeStatement):
				# add the include file to the fileset
				file =            self._rootDirectory / stmt.FileName
				includeFile =     self._classFileListFile(file) #self._classFileListFile only available via late binding
				self._fileSet.AddFile(includeFile) #self._fileSet only available via late binding
				includeFile.Parse()
				
				self._includes.append(includeFile)
				for srcFile in includeFile.Files:
					self._files.append(srcFile)
				for lib in includeFile.Libraries:
					self._libraries.append(lib)
				for warn in includeFile.Warnings:
					self._warnings.append(warn)
			elif isinstance(stmt, LibraryStatement):
				lib =          self._rootDirectory / stmt.DirectoryName
				vhdlLibRef =  VHDLLibraryReference(stmt.Library, lib)
				self._libraries.append(vhdlLibRef)
			elif isinstance(stmt, IfElseIfElseStatement):
				exprValue = self._Evaluate(stmt.IfClause.Expression)
				if (exprValue is True):
					self._Resolve(stmt.IfClause.Statements)
				elif (stmt.ElseIfClauses is not None):
					for elseif in stmt.ElseIfClauses:
						exprValue = self._Evaluate(elseif.Expression)
						if (exprValue is True):
							self._Resolve(elseif.Statements)
							break
				if ((exprValue is False) and (stmt.ElseClause is not None)):
					self._Resolve(stmt.ElseClause.Statements)
			elif isinstance(stmt, ReportStatement):
				self._warnings.append("WARNING: {0}".format(stmt.Message))
			else:
				ParserException("Found unknown statement type '{0}'.".format(stmt.__class__.__name__))
	
	def _Evaluate(self, expr):
		if isinstance(expr, Identifier):
			try:
				return self._variables[expr.Name] #self._variables only available via late binding
			except KeyError as ex:                        raise ParserException("Identifier '{0}' not found.".format(expr.Name)) from ex
		elif isinstance(expr, StringLiteral):
			return expr.Value
		elif isinstance(expr, IntegerLiteral):
			return expr.Value
		elif isinstance(expr, ExistsFunction):
			return (self._rootDirectory / expr.Path).exists()
		elif isinstance(expr, ListConstructorExpression):
			return [self._Evaluate(item) for item in expr.List]
		elif isinstance(expr, NotExpression):
			return not self._Evaluate(expr.Child)
		elif isinstance(expr, InExpression):
			return self._Evaluate(expr.LeftChild) in self._Evaluate(expr.RightChild)
		elif isinstance(expr, NotInExpression):
			return self._Evaluate(expr.LeftChild) not in self._Evaluate(expr.RightChild)
		elif isinstance(expr, AndExpression):
			return self._Evaluate(expr.LeftChild) and self._Evaluate(expr.RightChild)
		elif isinstance(expr, OrExpression):
			return self._Evaluate(expr.LeftChild) or self._Evaluate(expr.RightChild)
		elif isinstance(expr, XorExpression):
			l = self._Evaluate(expr.LeftChild)
			r = self._Evaluate(expr.RightChild)
			return (not l and r) or (l and not r)
		elif isinstance(expr, EqualExpression):
			return self._Evaluate(expr.LeftChild) == self._Evaluate(expr.RightChild)
		elif isinstance(expr, UnequalExpression):
			return self._Evaluate(expr.LeftChild) != self._Evaluate(expr.RightChild)
		elif isinstance(expr, LessThanExpression):
			return self._Evaluate(expr.LeftChild) < self._Evaluate(expr.RightChild)
		elif isinstance(expr, LessThanEqualExpression):
			return self._Evaluate(expr.LeftChild) <= self._Evaluate(expr.RightChild)
		elif isinstance(expr, GreaterThanExpression):
			return self._Evaluate(expr.LeftChild) > self._Evaluate(expr.RightChild)
		elif isinstance(expr, GreaterThanEqualExpression):
			return self._Evaluate(expr.LeftChild) >= self._Evaluate(expr.RightChild)
		else:                                            raise ParserException("Unsupported expression type '{0}'".format(type(expr)))

	@property
	def Files(self):      return self._files
	@property
	def Includes(self):   return self._includes
	@property	
	def Libraries(self):  return self._libraries
	@property
	def Warnings(self):   return self._warnings

	def __str__(self):    return "FILES file: '{0!s}'".format(self._file) #self._file only available via late binding
	def __repr__(self):   return self.__str__()
