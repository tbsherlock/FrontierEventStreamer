// Move bytecode v6
module d12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75.access {
use 0000000000000000000000000000000000000000000000000000000000000001::ascii;
use 0000000000000000000000000000000000000000000000000000000000000001::option;
use 0000000000000000000000000000000000000000000000000000000000000001::type_name;
use 0000000000000000000000000000000000000000000000000000000000000002::event;
use 0000000000000000000000000000000000000000000000000000000000000002::object;
use 0000000000000000000000000000000000000000000000000000000000000002::table;
use 0000000000000000000000000000000000000000000000000000000000000002::transfer;
use 0000000000000000000000000000000000000000000000000000000000000002::tx_context;
use d12a70c74c1e759445d6f209b01d43d860e97fcf2ef72ccbbd00afd828043f75::world;

struct ReturnOwnerCapReceipt {
	owner_id: address,
	owner_cap_id: ID
}

struct AdminACL has key {
	id: UID,
	authorized_sponsors: Table<address, bool>
}

struct OwnerCap<phantom Ty0> has key {
	id: UID,
	authorized_object_id: ID
}

struct ServerAddressRegistry has key {
	id: UID,
	authorized_address: Table<address, bool>
}

struct OwnerCapCreatedEvent has copy, drop {
	owner_cap_id: ID,
	authorized_object_id: ID
}

struct OwnerCapTransferred has copy, drop {
	owner_cap_id: ID,
	authorized_object_id: ID,
	previous_owner: address,
	owner: address
}

init(Arg0: &mut TxContext) {
L1:	loc0: AdminACL
L2:	loc1: ServerAddressRegistry
B0:
	0: CopyLoc[0](Arg0: &mut TxContext)
	1: Call object::new(&mut TxContext): UID
	2: CopyLoc[0](Arg0: &mut TxContext)
	3: Call table::new<address, bool>(&mut TxContext): Table<address, bool>
	4: Pack[3](ServerAddressRegistry)
	5: StLoc[2](loc1: ServerAddressRegistry)
	6: CopyLoc[0](Arg0: &mut TxContext)
	7: Call object::new(&mut TxContext): UID
	8: MoveLoc[0](Arg0: &mut TxContext)
	9: Call table::new<address, bool>(&mut TxContext): Table<address, bool>
	10: Pack[1](AdminACL)
	11: StLoc[1](loc0: AdminACL)
	12: MoveLoc[2](loc1: ServerAddressRegistry)
	13: Call transfer::share_object<ServerAddressRegistry>(ServerAddressRegistry)
	14: MoveLoc[1](loc0: AdminACL)
	15: Call transfer::share_object<AdminACL>(AdminACL)
	16: Ret
}

public transfer_owner_cap<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: address) {
B0:
	0: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	1: MoveLoc[1](Arg1: address)
	2: Call transfer::transfer<OwnerCap<Ty0>>(OwnerCap<Ty0>, address)
	3: Ret
}

public transfer_owner_cap_to_address<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: address, Arg2: &mut TxContext) {
L3:	loc0: bool
L4:	loc1: TypeName
B0:
	0: Call type_name::with_defining_ids<Ty0>(): TypeName
	1: StLoc[4](loc1: TypeName)
	2: ImmBorrowLoc[4](loc1: TypeName)
	3: Call type_name::module_string(&TypeName): String
	4: LdConst[8](vector<u8>: "cha..)
	5: Call ascii::string(vector<u8>): String
	6: Eq
	7: BrFalse(15)
B1:
	8: ImmBorrowLoc[4](loc1: TypeName)
	9: Call type_name::datatype_string(&TypeName): String
	10: LdConst[9](vector<u8>: "Cha..)
	11: Call ascii::string(vector<u8>): String
	12: Eq
	13: StLoc[3](loc0: bool)
	14: Branch(17)
B2:
	15: LdFalse
	16: StLoc[3](loc0: bool)
B3:
	17: MoveLoc[3](loc0: bool)
	18: Not
	19: BrFalse(21)
B4:
	20: Branch(25)
B5:
	21: MoveLoc[2](Arg2: &mut TxContext)
	22: Pop
	23: LdU64(13835058544908435457)
	24: Abort
B6:
	25: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	26: MoveLoc[2](Arg2: &mut TxContext)
	27: FreezeRef
	28: Call tx_context::sender(&TxContext): address
	29: MoveLoc[1](Arg1: address)
	30: Call transfer<Ty0>(OwnerCap<Ty0>, address, address)
	31: Ret
}

public return_owner_cap_to_object<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: ReturnOwnerCapReceipt, Arg2: address) {
B0:
	0: MoveLoc[1](Arg1: ReturnOwnerCapReceipt)
	1: ImmBorrowLoc[0](Arg0: OwnerCap<Ty0>)
	2: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	3: CopyLoc[2](Arg2: address)
	4: Call validate_return_receipt(ReturnOwnerCapReceipt, ID, address)
	5: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	6: MoveLoc[2](Arg2: address)
	7: Call transfer_owner_cap<Ty0>(OwnerCap<Ty0>, address)
	8: Ret
}

public transfer_owner_cap_with_receipt<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: ReturnOwnerCapReceipt, Arg2: address, Arg3: &mut TxContext) {
L4:	loc0: ID
B0:
	0: MoveLoc[1](Arg1: ReturnOwnerCapReceipt)
	1: Unpack[0](ReturnOwnerCapReceipt)
	2: StLoc[4](loc0: ID)
	3: Pop
	4: MoveLoc[4](loc0: ID)
	5: ImmBorrowLoc[0](Arg0: OwnerCap<Ty0>)
	6: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	7: Eq
	8: BrFalse(10)
B1:
	9: Branch(14)
B2:
	10: MoveLoc[3](Arg3: &mut TxContext)
	11: Pop
	12: LdU64(13835903064328241159)
	13: Abort
B3:
	14: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	15: MoveLoc[2](Arg2: address)
	16: MoveLoc[3](Arg3: &mut TxContext)
	17: Call transfer_owner_cap_to_address<Ty0>(OwnerCap<Ty0>, address, &mut TxContext)
	18: Ret
}

public is_authorized_server_address(Arg0: &ServerAddressRegistry, Arg1: address): bool {
B0:
	0: MoveLoc[0](Arg0: &ServerAddressRegistry)
	1: ImmBorrowField[0](ServerAddressRegistry.authorized_address: Table<address, bool>)
	2: MoveLoc[1](Arg1: address)
	3: Call table::contains<address, bool>(&Table<address, bool>, address): bool
	4: Ret
}

public is_authorized<Ty0: key>(Arg0: &OwnerCap<Ty0>, Arg1: ID): bool {
B0:
	0: MoveLoc[0](Arg0: &OwnerCap<Ty0>)
	1: ImmBorrowFieldGeneric[0](OwnerCap.authorized_object_id: ID)
	2: ReadRef
	3: MoveLoc[1](Arg1: ID)
	4: Eq
	5: Ret
}

public verify_sponsor(Arg0: &AdminACL, Arg1: &TxContext) {
L2:	loc0: address
L3:	loc1: address
L4:	loc2: Option<address>
B0:
	0: CopyLoc[1](Arg1: &TxContext)
	1: Call tx_context::sponsor(&TxContext): Option<address>
	2: StLoc[4](loc2: Option<address>)
	3: ImmBorrowLoc[4](loc2: Option<address>)
	4: Call option::is_some<address>(&Option<address>): bool
	5: BrFalse(13)
B1:
	6: MoveLoc[1](Arg1: &TxContext)
	7: Pop
	8: ImmBorrowLoc[4](loc2: Option<address>)
	9: Call option::borrow<address>(&Option<address>): &address
	10: ReadRef
	11: StLoc[2](loc0: address)
	12: Branch(16)
B2:
	13: MoveLoc[1](Arg1: &TxContext)
	14: Call tx_context::sender(&TxContext): address
	15: StLoc[2](loc0: address)
B3:
	16: MoveLoc[2](loc0: address)
	17: StLoc[3](loc1: address)
	18: MoveLoc[0](Arg0: &AdminACL)
	19: ImmBorrowField[2](AdminACL.authorized_sponsors: Table<address, bool>)
	20: MoveLoc[3](loc1: address)
	21: Call table::contains<address, bool>(&Table<address, bool>, address): bool
	22: BrFalse(24)
B4:
	23: Branch(26)
B5:
	24: LdU64(13835340234633641987)
	25: Abort
B6:
	26: Ret
}

public(friend) create_and_transfer_owner_cap<Ty0: key>(Arg0: ID, Arg1: &AdminACL, Arg2: address, Arg3: &mut TxContext): ID {
L4:	loc0: OwnerCap<Ty0>
L5:	loc1: ID
B0:
	0: MoveLoc[0](Arg0: ID)
	1: MoveLoc[1](Arg1: &AdminACL)
	2: MoveLoc[3](Arg3: &mut TxContext)
	3: Call create_owner_cap_by_id<Ty0>(ID, &AdminACL, &mut TxContext): OwnerCap<Ty0>
	4: StLoc[4](loc0: OwnerCap<Ty0>)
	5: ImmBorrowLoc[4](loc0: OwnerCap<Ty0>)
	6: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	7: StLoc[5](loc1: ID)
	8: MoveLoc[4](loc0: OwnerCap<Ty0>)
	9: LdConst[10](address: 0x00..)
	10: MoveLoc[2](Arg2: address)
	11: Call transfer<Ty0>(OwnerCap<Ty0>, address, address)
	12: MoveLoc[5](loc1: ID)
	13: Ret
}

public(friend) receive_owner_cap<Ty0: key>(Arg0: &mut UID, Arg1: Receiving<OwnerCap<Ty0>>): OwnerCap<Ty0> {
B0:
	0: MoveLoc[0](Arg0: &mut UID)
	1: MoveLoc[1](Arg1: Receiving<OwnerCap<Ty0>>)
	2: Call transfer::receive<OwnerCap<Ty0>>(&mut UID, Receiving<OwnerCap<Ty0>>): OwnerCap<Ty0>
	3: Ret
}

public(friend) create_return_receipt(Arg0: ID, Arg1: address): ReturnOwnerCapReceipt {
B0:
	0: MoveLoc[1](Arg1: address)
	1: MoveLoc[0](Arg0: ID)
	2: Pack[0](ReturnOwnerCapReceipt)
	3: Ret
}

public add_sponsor_to_acl(Arg0: &mut AdminACL, Arg1: &GovernorCap, Arg2: address) {
B0:
	0: MoveLoc[0](Arg0: &mut AdminACL)
	1: MutBorrowField[2](AdminACL.authorized_sponsors: Table<address, bool>)
	2: MoveLoc[2](Arg2: address)
	3: LdTrue
	4: Call table::add<address, bool>(&mut Table<address, bool>, address, bool)
	5: Ret
}

public create_owner_cap<Ty0: key>(Arg0: &AdminACL, Arg1: &Ty0, Arg2: &mut TxContext): OwnerCap<Ty0> {
L3:	loc0: ID
L4:	loc1: OwnerCap<Ty0>
B0:
	0: MoveLoc[0](Arg0: &AdminACL)
	1: CopyLoc[2](Arg2: &mut TxContext)
	2: FreezeRef
	3: Call verify_sponsor(&AdminACL, &TxContext)
	4: MoveLoc[1](Arg1: &Ty0)
	5: Call object::id<Ty0>(&Ty0): ID
	6: StLoc[3](loc0: ID)
	7: MoveLoc[2](Arg2: &mut TxContext)
	8: Call object::new(&mut TxContext): UID
	9: CopyLoc[3](loc0: ID)
	10: PackGeneric[0](OwnerCap<Ty0>)
	11: StLoc[4](loc1: OwnerCap<Ty0>)
	12: ImmBorrowLoc[4](loc1: OwnerCap<Ty0>)
	13: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	14: MoveLoc[3](loc0: ID)
	15: Pack[4](OwnerCapCreatedEvent)
	16: Call event::emit<OwnerCapCreatedEvent>(OwnerCapCreatedEvent)
	17: MoveLoc[4](loc1: OwnerCap<Ty0>)
	18: Ret
}

public create_owner_cap_by_id<Ty0: key>(Arg0: ID, Arg1: &AdminACL, Arg2: &mut TxContext): OwnerCap<Ty0> {
L3:	loc0: OwnerCap<Ty0>
B0:
	0: MoveLoc[1](Arg1: &AdminACL)
	1: CopyLoc[2](Arg2: &mut TxContext)
	2: FreezeRef
	3: Call verify_sponsor(&AdminACL, &TxContext)
	4: MoveLoc[2](Arg2: &mut TxContext)
	5: Call object::new(&mut TxContext): UID
	6: CopyLoc[0](Arg0: ID)
	7: PackGeneric[0](OwnerCap<Ty0>)
	8: StLoc[3](loc0: OwnerCap<Ty0>)
	9: ImmBorrowLoc[3](loc0: OwnerCap<Ty0>)
	10: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	11: MoveLoc[0](Arg0: ID)
	12: Pack[4](OwnerCapCreatedEvent)
	13: Call event::emit<OwnerCapCreatedEvent>(OwnerCapCreatedEvent)
	14: MoveLoc[3](loc0: OwnerCap<Ty0>)
	15: Ret
}

public register_server_address(Arg0: &mut ServerAddressRegistry, Arg1: &GovernorCap, Arg2: address) {
B0:
	0: MoveLoc[0](Arg0: &mut ServerAddressRegistry)
	1: MutBorrowField[0](ServerAddressRegistry.authorized_address: Table<address, bool>)
	2: MoveLoc[2](Arg2: address)
	3: LdTrue
	4: Call table::add<address, bool>(&mut Table<address, bool>, address, bool)
	5: Ret
}

public remove_server_address(Arg0: &mut ServerAddressRegistry, Arg1: &GovernorCap, Arg2: address) {
B0:
	0: MoveLoc[0](Arg0: &mut ServerAddressRegistry)
	1: MutBorrowField[0](ServerAddressRegistry.authorized_address: Table<address, bool>)
	2: MoveLoc[2](Arg2: address)
	3: Call table::remove<address, bool>(&mut Table<address, bool>, address): bool
	4: Pop
	5: Ret
}

public delete_owner_cap<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: &AdminACL, Arg2: &TxContext) {
B0:
	0: MoveLoc[1](Arg1: &AdminACL)
	1: MoveLoc[2](Arg2: &TxContext)
	2: Call verify_sponsor(&AdminACL, &TxContext)
	3: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	4: UnpackGeneric[0](OwnerCap<Ty0>)
	5: Pop
	6: Call object::delete(UID)
	7: Ret
}

transfer<Ty0: key>(Arg0: OwnerCap<Ty0>, Arg1: address, Arg2: address) {
B0:
	0: ImmBorrowLoc[0](Arg0: OwnerCap<Ty0>)
	1: Call object::id<OwnerCap<Ty0>>(&OwnerCap<Ty0>): ID
	2: ImmBorrowLoc[0](Arg0: OwnerCap<Ty0>)
	3: ImmBorrowFieldGeneric[0](OwnerCap.authorized_object_id: ID)
	4: ReadRef
	5: MoveLoc[1](Arg1: address)
	6: CopyLoc[2](Arg2: address)
	7: Pack[5](OwnerCapTransferred)
	8: Call event::emit<OwnerCapTransferred>(OwnerCapTransferred)
	9: MoveLoc[0](Arg0: OwnerCap<Ty0>)
	10: MoveLoc[2](Arg2: address)
	11: Call transfer::transfer<OwnerCap<Ty0>>(OwnerCap<Ty0>, address)
	12: Ret
}

validate_return_receipt(Arg0: ReturnOwnerCapReceipt, Arg1: ID, Arg2: address) {
L3:	loc0: ID
B0:
	0: MoveLoc[0](Arg0: ReturnOwnerCapReceipt)
	1: Unpack[0](ReturnOwnerCapReceipt)
	2: StLoc[3](loc0: ID)
	3: MoveLoc[2](Arg2: address)
	4: Eq
	5: BrFalse(7)
B1:
	6: Branch(9)
B2:
	7: LdU64(13835622220711591941)
	8: Abort
B3:
	9: MoveLoc[3](loc0: ID)
	10: MoveLoc[1](Arg1: ID)
	11: Eq
	12: BrFalse(14)
B4:
	13: Branch(16)
B5:
	14: LdU64(13835903699983400967)
	15: Abort
B6:
	16: Ret
}

Constants [
	0 => vector<u8>: "ECharacterTransfer" // interpreted as UTF8 string
	1 => vector<u8>: "Character cannot be transferred" // interpreted as UTF8 string
	2 => vector<u8>: "EUnauthorizedSponsor" // interpreted as UTF8 string
	3 => vector<u8>: "Unauthorized sponsor" // interpreted as UTF8 string
	4 => vector<u8>: "EOwnerIdMismatch" // interpreted as UTF8 string
	5 => vector<u8>: "Owner ID mismatch" // interpreted as UTF8 string
	6 => vector<u8>: "EOwnerCapIdMismatch" // interpreted as UTF8 string
	7 => vector<u8>: "Owner Cap ID mismatch" // interpreted as UTF8 string
	8 => vector<u8>: "character" // interpreted as UTF8 string
	9 => vector<u8>: "Character" // interpreted as UTF8 string
	10 => address: 0x0000000000000000000000000000000000000000000000000000000000000000
]
}
