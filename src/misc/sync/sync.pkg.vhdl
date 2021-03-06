-- EMACS settings: -*-  tab-width: 2; indent-tabs-mode: t -*-
-- vim: tabstop=2:shiftwidth=2:noexpandtab
-- kate: tab-width 2; replace-tabs off; indent-width 2;
--
-- ============================================================================
-- Authors:					Patrick Lehmann
--
-- Package:					VHDL package for component declarations, types and
--									functions associated to the PoC.misc.sync namespace
--
-- Description:
-- ------------------------------------
--		For detailed documentation see below.
--
-- License:
-- ============================================================================
-- Copyright 2007-2016 Technische Universitaet Dresden - Germany,
--										 Chair for VLSI-Design, Diagnostics and Architecture
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--		http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
-- ============================================================================

library IEEE;
use			IEEE.STD_LOGIC_1164.all;
use			IEEE.NUMERIC_STD.all;


package sync is
	subtype T_MISC_SYNC_DEPTH		is INTEGER range 2 to 16;

	component sync_Bits is
		generic (
			BITS					: POSITIVE						:= 1;									-- number of bit to be synchronized
			INIT					: STD_LOGIC_VECTOR		:= x"00000000";				-- initialitation bits
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2									-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;														-- <Clock>	output clock domain
			Input					: in	STD_LOGIC_VECTOR(BITS - 1 downto 0);	-- @async:	input bits
			Output				: out STD_LOGIC_VECTOR(BITS - 1 downto 0)		-- @Clock:	output bits
		);
	end component;

	component sync_Bits_Altera is
		generic (
			BITS					: POSITIVE						:= 1;									-- number of bit to be synchronized
			INIT					: STD_LOGIC_VECTOR		:= x"00000000";				-- initialitation bits
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2									-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;														-- Clock to be synchronized to
			Input					: in	STD_LOGIC_VECTOR(BITS - 1 downto 0);	-- Data to be synchronized
			Output				: out	STD_LOGIC_VECTOR(BITS - 1 downto 0)		-- synchronised data
		);
	end component;

	component sync_Bits_Xilinx is
		generic (
			BITS					: POSITIVE						:= 1;									-- number of bit to be synchronized
			INIT					: STD_LOGIC_VECTOR		:= x"00000000";				-- initialitation bits
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2									-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;														-- Clock to be synchronized to
			Input					: in	STD_LOGIC_VECTOR(BITS - 1 downto 0);	-- Data to be synchronized
			Output				: out	STD_LOGIC_VECTOR(BITS - 1 downto 0)		-- synchronised data
		);
	end component;

	component sync_Reset is
		generic (
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2		-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;							-- <Clock>	output clock domain
			Input					: in	STD_LOGIC;							-- @async:	reset input
			Output				: out STD_LOGIC								-- @Clock:	reset output
		);
	end component;

	component sync_Reset_Altera is
		generic (
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2		-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;							-- <Clock>	output clock domain
			Input					: in	STD_LOGIC;							-- @async:	reset input
			Output				: out STD_LOGIC								-- @Clock:	reset output
		);
	end component;

	component sync_Reset_Xilinx is
		generic (
			SYNC_DEPTH		: T_MISC_SYNC_DEPTH		:= 2		-- generate SYNC_DEPTH many stages, at least 2
		);
		port (
			Clock					: in	STD_LOGIC;							-- <Clock>	output clock domain
			Input					: in	STD_LOGIC;							-- @async:	reset input
			Output				: out STD_LOGIC								-- @Clock:	reset output
		);
	end component;
end package;
