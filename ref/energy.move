// Move bytecode v6
module d12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75.energy {
use 0000000000000000000000000000000000000000000000000000000000000002::event;
use 0000000000000000000000000000000000000000000000000000000000000002::object;
use 0000000000000000000000000000000000000000000000000000000000000002::table;
use 0000000000000000000000000000000000000000000000000000000000000002::transfer;
use 0000000000000000000000000000000000000000000000000000000000000002::tx_context;
use d12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75::access;

struct EnergyConfig has key {
	id: UID,
	assembly_energy: Table<u64, u64>
}

struct EnergySource has store {
	max_energy_production: u64,
	current_energy_production: u64,
	total_reserved_energy: u64
}

struct StartEnergyProductionEvent has copy, drop {
	energy_source_id: ID,
	current_energy_production: u64
}

struct StopEnergyProductionEvent has copy, drop {
	energy_source_id: ID
}

struct EnergyReservedEvent has copy, drop {
	energy_source_id: ID,
	assembly_type_id: u64,
	energy_reserved: u64,
	total_reserved_energy: u64
}

struct EnergyReleasedEvent has copy, drop {
	energy_source_id: ID,
	assembly_type_id: u64,
	energy_released: u64,
	total_reserved_energy: u64
}

public assembly_energy(Arg0: &EnergyConfig, Arg1: u64): u64 {
L2:	loc0: u64
B0:
	0: CopyLoc[1](Arg1: u64)
	1: LdU64(0)
	2: Neq
	3: BrFalse(5)
B1:
	4: Branch(9)
B2:
	5: MoveLoc[0](Arg0: &EnergyConfig)
	6: Pop
	7: LdU64(13835058321570136065)
	8: Abort
B3:
	9: CopyLoc[0](Arg0: &EnergyConfig)
	10: ImmBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	11: CopyLoc[1](Arg1: u64)
	12: Call table::contains<u64, u64>(&Table<u64, u64>, u64): bool
	13: BrFalse(21)
B4:
	14: MoveLoc[0](Arg0: &EnergyConfig)
	15: ImmBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	16: MoveLoc[1](Arg1: u64)
	17: Call table::borrow<u64, u64>(&Table<u64, u64>, u64): &u64
	18: ReadRef
	19: StLoc[2](loc0: u64)
	20: Branch(25)
B5:
	21: MoveLoc[0](Arg0: &EnergyConfig)
	22: Pop
	23: LdU64(0)
	24: StLoc[2](loc0: u64)
B6:
	25: MoveLoc[2](loc0: u64)
	26: Ret
}

public total_reserved_energy(Arg0: &EnergySource): u64 {
B0:
	0: MoveLoc[0](Arg0: &EnergySource)
	1: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	2: ReadRef
	3: Ret
}

public available_energy(Arg0: &EnergySource): u64 {
L1:	loc0: u64
B0:
	0: CopyLoc[0](Arg0: &EnergySource)
	1: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	2: ReadRef
	3: CopyLoc[0](Arg0: &EnergySource)
	4: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	5: ReadRef
	6: Gt
	7: BrFalse(17)
B1:
	8: CopyLoc[0](Arg0: &EnergySource)
	9: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	10: ReadRef
	11: MoveLoc[0](Arg0: &EnergySource)
	12: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	13: ReadRef
	14: Sub
	15: StLoc[1](loc0: u64)
	16: Branch(21)
B2:
	17: MoveLoc[0](Arg0: &EnergySource)
	18: Pop
	19: LdU64(0)
	20: StLoc[1](loc0: u64)
B3:
	21: MoveLoc[1](loc0: u64)
	22: Ret
}

public current_energy_production(Arg0: &EnergySource): u64 {
B0:
	0: MoveLoc[0](Arg0: &EnergySource)
	1: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	2: ReadRef
	3: Ret
}

public max_energy_production(Arg0: &EnergySource): u64 {
B0:
	0: MoveLoc[0](Arg0: &EnergySource)
	1: ImmBorrowField[3](EnergySource.max_energy_production: u64)
	2: ReadRef
	3: Ret
}

public set_energy_config(Arg0: &mut EnergyConfig, Arg1: &AdminACL, Arg2: u64, Arg3: u64, Arg4: &TxContext) {
B0:
	0: MoveLoc[1](Arg1: &AdminACL)
	1: MoveLoc[4](Arg4: &TxContext)
	2: Call access::verify_sponsor(&AdminACL, &TxContext)
	3: CopyLoc[2](Arg2: u64)
	4: LdU64(0)
	5: Neq
	6: BrFalse(8)
B1:
	7: Branch(12)
B2:
	8: MoveLoc[0](Arg0: &mut EnergyConfig)
	9: Pop
	10: LdU64(13835058501958762497)
	11: Abort
B3:
	12: CopyLoc[3](Arg3: u64)
	13: LdU64(0)
	14: Gt
	15: BrFalse(17)
B4:
	16: Branch(21)
B5:
	17: MoveLoc[0](Arg0: &mut EnergyConfig)
	18: Pop
	19: LdU64(13835339981230571523)
	20: Abort
B6:
	21: CopyLoc[0](Arg0: &mut EnergyConfig)
	22: ImmBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	23: CopyLoc[2](Arg2: u64)
	24: Call table::contains<u64, u64>(&Table<u64, u64>, u64): bool
	25: BrFalse(31)
B7:
	26: CopyLoc[0](Arg0: &mut EnergyConfig)
	27: MutBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	28: CopyLoc[2](Arg2: u64)
	29: Call table::remove<u64, u64>(&mut Table<u64, u64>, u64): u64
	30: Pop
B8:
	31: MoveLoc[0](Arg0: &mut EnergyConfig)
	32: MutBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	33: MoveLoc[2](Arg2: u64)
	34: MoveLoc[3](Arg3: u64)
	35: Call table::add<u64, u64>(&mut Table<u64, u64>, u64, u64)
	36: Ret
}

public remove_energy_config(Arg0: &mut EnergyConfig, Arg1: &AdminACL, Arg2: u64, Arg3: &TxContext) {
B0:
	0: MoveLoc[1](Arg1: &AdminACL)
	1: MoveLoc[3](Arg3: &TxContext)
	2: Call access::verify_sponsor(&AdminACL, &TxContext)
	3: CopyLoc[2](Arg2: u64)
	4: LdU64(0)
	5: Neq
	6: BrFalse(8)
B1:
	7: Branch(12)
B2:
	8: MoveLoc[0](Arg0: &mut EnergyConfig)
	9: Pop
	10: LdU64(13835058574973206529)
	11: Abort
B3:
	12: CopyLoc[0](Arg0: &mut EnergyConfig)
	13: ImmBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	14: CopyLoc[2](Arg2: u64)
	15: Call table::contains<u64, u64>(&Table<u64, u64>, u64): bool
	16: BrFalse(18)
B4:
	17: Branch(22)
B5:
	18: MoveLoc[0](Arg0: &mut EnergyConfig)
	19: Pop
	20: LdU64(13835621529221857285)
	21: Abort
B6:
	22: MoveLoc[0](Arg0: &mut EnergyConfig)
	23: MutBorrowField[0](EnergyConfig.assembly_energy: Table<u64, u64>)
	24: MoveLoc[2](Arg2: u64)
	25: Call table::remove<u64, u64>(&mut Table<u64, u64>, u64): u64
	26: Pop
	27: Ret
}

public(friend) create(Arg0: u64): EnergySource {
B0:
	0: CopyLoc[0](Arg0: u64)
	1: LdU64(0)
	2: Gt
	3: BrFalse(5)
B1:
	4: Branch(7)
B2:
	5: LdU64(13836184509240311817)
	6: Abort
B3:
	7: MoveLoc[0](Arg0: u64)
	8: LdU64(0)
	9: LdU64(0)
	10: Pack[1](EnergySource)
	11: Ret
}

public(friend) start_energy_production(Arg0: &mut EnergySource, Arg1: ID) {
B0:
	0: CopyLoc[0](Arg0: &mut EnergySource)
	1: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	2: ReadRef
	3: LdU64(0)
	4: Eq
	5: BrFalse(7)
B1:
	6: Branch(11)
B2:
	7: MoveLoc[0](Arg0: &mut EnergySource)
	8: Pop
	9: LdU64(13836747515028570125)
	10: Abort
B3:
	11: CopyLoc[0](Arg0: &mut EnergySource)
	12: ImmBorrowField[3](EnergySource.max_energy_production: u64)
	13: ReadRef
	14: CopyLoc[0](Arg0: &mut EnergySource)
	15: MutBorrowField[2](EnergySource.current_energy_production: u64)
	16: WriteRef
	17: MoveLoc[1](Arg1: ID)
	18: MoveLoc[0](Arg0: &mut EnergySource)
	19: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	20: ReadRef
	21: Pack[2](StartEnergyProductionEvent)
	22: Call event::emit<StartEnergyProductionEvent>(StartEnergyProductionEvent)
	23: Ret
}

public(friend) stop_energy_production(Arg0: &mut EnergySource, Arg1: ID) {
B0:
	0: CopyLoc[0](Arg0: &mut EnergySource)
	1: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	2: ReadRef
	3: LdU64(0)
	4: Gt
	5: BrFalse(7)
B1:
	6: Branch(11)
B2:
	7: MoveLoc[0](Arg0: &mut EnergySource)
	8: Pop
	9: LdU64(13836466078706434059)
	10: Abort
B3:
	11: LdU64(0)
	12: CopyLoc[0](Arg0: &mut EnergySource)
	13: MutBorrowField[2](EnergySource.current_energy_production: u64)
	14: WriteRef
	15: LdU64(0)
	16: MoveLoc[0](Arg0: &mut EnergySource)
	17: MutBorrowField[1](EnergySource.total_reserved_energy: u64)
	18: WriteRef
	19: MoveLoc[1](Arg1: ID)
	20: Pack[3](StopEnergyProductionEvent)
	21: Call event::emit<StopEnergyProductionEvent>(StopEnergyProductionEvent)
	22: Ret
}

public(friend) reserve_energy(Arg0: &mut EnergySource, Arg1: ID, Arg2: &EnergyConfig, Arg3: u64) {
L4:	loc0: u64
B0:
	0: CopyLoc[3](Arg3: u64)
	1: LdU64(0)
	2: Neq
	3: BrFalse(5)
B1:
	4: Branch(11)
B2:
	5: MoveLoc[0](Arg0: &mut EnergySource)
	6: Pop
	7: MoveLoc[2](Arg2: &EnergyConfig)
	8: Pop
	9: LdU64(13835058772541702145)
	10: Abort
B3:
	11: CopyLoc[0](Arg0: &mut EnergySource)
	12: ImmBorrowField[2](EnergySource.current_energy_production: u64)
	13: ReadRef
	14: LdU64(0)
	15: Gt
	16: BrFalse(18)
B4:
	17: Branch(24)
B5:
	18: MoveLoc[0](Arg0: &mut EnergySource)
	19: Pop
	20: MoveLoc[2](Arg2: &EnergyConfig)
	21: Pop
	22: LdU64(13836466151720878091)
	23: Abort
B6:
	24: MoveLoc[2](Arg2: &EnergyConfig)
	25: CopyLoc[3](Arg3: u64)
	26: Call assembly_energy(&EnergyConfig, u64): u64
	27: StLoc[4](loc0: u64)
	28: CopyLoc[0](Arg0: &mut EnergySource)
	29: FreezeRef
	30: Call available_energy(&EnergySource): u64
	31: CopyLoc[4](loc0: u64)
	32: Ge
	33: BrFalse(35)
B7:
	34: Branch(39)
B8:
	35: MoveLoc[0](Arg0: &mut EnergySource)
	36: Pop
	37: LdU64(13835903218947063815)
	38: Abort
B9:
	39: CopyLoc[0](Arg0: &mut EnergySource)
	40: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	41: ReadRef
	42: CopyLoc[4](loc0: u64)
	43: Add
	44: CopyLoc[0](Arg0: &mut EnergySource)
	45: MutBorrowField[1](EnergySource.total_reserved_energy: u64)
	46: WriteRef
	47: MoveLoc[1](Arg1: ID)
	48: MoveLoc[3](Arg3: u64)
	49: MoveLoc[4](loc0: u64)
	50: MoveLoc[0](Arg0: &mut EnergySource)
	51: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	52: ReadRef
	53: Pack[4](EnergyReservedEvent)
	54: Call event::emit<EnergyReservedEvent>(EnergyReservedEvent)
	55: Ret
}

public(friend) release_energy(Arg0: &mut EnergySource, Arg1: ID, Arg2: &EnergyConfig, Arg3: u64) {
L4:	loc0: bool
L5:	loc1: u64
B0:
	0: CopyLoc[3](Arg3: u64)
	1: LdU64(0)
	2: Neq
	3: BrFalse(5)
B1:
	4: Branch(11)
B2:
	5: MoveLoc[0](Arg0: &mut EnergySource)
	6: Pop
	7: MoveLoc[2](Arg2: &EnergyConfig)
	8: Pop
	9: LdU64(13835058875620917249)
	10: Abort
B3:
	11: MoveLoc[2](Arg2: &EnergyConfig)
	12: CopyLoc[3](Arg3: u64)
	13: Call assembly_energy(&EnergyConfig, u64): u64
	14: StLoc[5](loc1: u64)
	15: CopyLoc[0](Arg0: &mut EnergySource)
	16: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	17: ReadRef
	18: LdU64(0)
	19: Eq
	20: BrFalse(24)
B4:
	21: LdTrue
	22: StLoc[4](loc0: bool)
	23: Branch(30)
B5:
	24: CopyLoc[0](Arg0: &mut EnergySource)
	25: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	26: ReadRef
	27: CopyLoc[5](loc1: u64)
	28: Lt
	29: StLoc[4](loc0: bool)
B6:
	30: MoveLoc[4](loc0: bool)
	31: BrFalse(35)
B7:
	32: MoveLoc[0](Arg0: &mut EnergySource)
	33: Pop
	34: Ret
B8:
	35: CopyLoc[0](Arg0: &mut EnergySource)
	36: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	37: ReadRef
	38: CopyLoc[5](loc1: u64)
	39: Sub
	40: CopyLoc[0](Arg0: &mut EnergySource)
	41: MutBorrowField[1](EnergySource.total_reserved_energy: u64)
	42: WriteRef
	43: MoveLoc[1](Arg1: ID)
	44: MoveLoc[3](Arg3: u64)
	45: MoveLoc[5](loc1: u64)
	46: MoveLoc[0](Arg0: &mut EnergySource)
	47: ImmBorrowField[1](EnergySource.total_reserved_energy: u64)
	48: ReadRef
	49: Pack[5](EnergyReleasedEvent)
	50: Call event::emit<EnergyReleasedEvent>(EnergyReleasedEvent)
	51: Ret
}

public(friend) delete(Arg0: EnergySource) {
B0:
	0: MoveLoc[0](Arg0: EnergySource)
	1: Unpack[1](EnergySource)
	2: Pop
	3: Pop
	4: Pop
	5: Ret
}

init(Arg0: &mut TxContext) {
B0:
	0: CopyLoc[0](Arg0: &mut TxContext)
	1: Call object::new(&mut TxContext): UID
	2: MoveLoc[0](Arg0: &mut TxContext)
	3: Call table::new<u64, u64>(&mut TxContext): Table<u64, u64>
	4: Pack[0](EnergyConfig)
	5: Call transfer::share_object<EnergyConfig>(EnergyConfig)
	6: Ret
}

Constants [
	0 => vector<u8>: "ETypeIdEmpty" // interpreted as UTF8 string
	1 => vector<u8>: "Assembly type id cannot be empty" // interpreted as UTF8 string
	2 => vector<u8>: "EInvalidEnergyAmount" // interpreted as UTF8 string
	3 => vector<u8>: "Energy amount must be greater than 0" // interpreted as UTF8 string
	4 => vector<u8>: "EIncorrectAssemblyType" // interpreted as UTF8 string
	5 => vector<u8>: "Energy requirement for this assembly type is not configured" // interpreted as UTF8 string
	6 => vector<u8>: "EInsufficientAvailableEnergy" // interpreted as UTF8 string
	7 => vector<u8>: "Insufficient available energy" // interpreted as UTF8 string
	8 => vector<u8>: "EInvalidMaxEnergyProduction" // interpreted as UTF8 string
	9 => vector<u8>: "Max energy production must be greater than 0" // interpreted as UTF8 string
	10 => vector<u8>: "ENotProducingEnergy" // interpreted as UTF8 string
	11 => vector<u8>: "Energy source is currently not producing energy" // interpreted as UTF8 string
	12 => vector<u8>: "EProducingEnergy" // interpreted as UTF8 string
	13 => vector<u8>: "Energy source is already producing energy" // interpreted as UTF8 string
]
}
