-- EMACS settings: -*-  tab-width: 2; indent-tabs-mode: t -*-
-- vim: tabstop=2:shiftwidth=2:noexpandtab
-- kate: tab-width 2; replace-tabs off; indent-width 2;
--
-- =============================================================================
-- Package:					TODO
--
-- Authors:					Patrick Lehmann
--
-- Description:
-- ------------------------------------
--		TODO
--
-- License:
-- =============================================================================
-- Copyright 2007-2014 Technische Universitaet Dresden - Germany
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
-- =============================================================================
library IEEE;
use			IEEE.STD_LOGIC_1164.all;

library PoC;
use			PoC.utils.all;


entity filter_or is
	generic (
		TAPS						: POSITIVE				:= 4;				--
		INIT						: STD_LOGIC				:= '1';			--
		ADD_OUTPUT_REG	: BOOLEAN					:= FALSE		--
	);
	port (
		Clock						: in	STD_LOGIC;							-- clock
		DataIn					: in	STD_LOGIC;							-- data to filter
		DataOut					: out	STD_LOGIC								-- filtered signal
	);
end;


architecture rtl of filter_or is
	signal Delays			: STD_LOGIC_VECTOR(TAPS - 1 downto 0)		:= (others => INIT);
	signal FilterOut	: STD_LOGIC;

begin
	Delays					<= Delays(Delays'high - 1 downto 0) & DataIn when rising_edge(Clock);
	FilterOut				<= slv_or(Delays);

	genOutReg0 : if (ADD_OUTPUT_REG = FALSE) generate
		DataOut				<= FilterOut;
	end generate;
	genOutReg1 : if (ADD_OUTPUT_REG = TRUE) generate
		signal FilterOut_d	: STD_LOGIC	:= INIT;
	begin
		FilterOut_d		<= FilterOut when rising_edge(Clock);
		DataOut				<= FilterOut_d;
	end generate;
end;