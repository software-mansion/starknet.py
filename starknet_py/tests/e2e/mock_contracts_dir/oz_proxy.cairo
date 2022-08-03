%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import (
    library_call,
    library_call_l1_handler,
    get_caller_address
)
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.cairo.common.math import assert_not_zero

#
# Constructor
#

@constructor
func constructor{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }(implementation_hash: felt):
    Proxy._set_implementation_hash(implementation_hash)
    return ()
end

#
# Fallback functions
#

@external
@raw_input
@raw_output
func __default__{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }(
        selector: felt,
        calldata_size: felt,
        calldata: felt*
    ) -> (
        retdata_size: felt,
        retdata: felt*
    ):
    let (class_hash) = Proxy.get_implementation_hash()

    let (retdata_size: felt, retdata: felt*) = library_call(
        class_hash=class_hash,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    )
    return (retdata_size=retdata_size, retdata=retdata)
end


@l1_handler
@raw_input
func __l1_default__{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    }(
        selector: felt,
        calldata_size: felt,
        calldata: felt*
    ):
    let (class_hash) = Proxy.get_implementation_hash()

    library_call_l1_handler(
        class_hash=class_hash,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    )
    return ()
end

#
# Events
#

@event
func Upgraded(implementation: felt):
end

@event
func AdminChanged(previousAdmin: felt, newAdmin: felt):
end

#
# Storage variables
#

@storage_var
func Proxy_implementation_hash() -> (class_hash: felt):
end

@storage_var
func Proxy_admin() -> (proxy_admin: felt):
end

@storage_var
func Proxy_initialized() -> (initialized: felt):
end

namespace Proxy:
    #
    # Initializer
    #

    func initializer{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }(proxy_admin: felt):
        let (initialized) = Proxy_initialized.read()
        with_attr error_message("Proxy: contract already initialized"):
            assert initialized = FALSE
        end

        Proxy_initialized.write(TRUE)
        _set_admin(proxy_admin)
        return ()
    end

    #
    # Guards
    #

    func assert_only_admin{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }():
        let (caller) = get_caller_address()
        let (admin) = Proxy_admin.read()
        with_attr error_message("Proxy: caller is not admin"):
            assert admin = caller
        end
        return ()
    end

    #
    # Getters
    #

    func get_implementation_hash{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }() -> (implementation: felt):
        let (implementation) = Proxy_implementation_hash.read()
        return (implementation)
    end

    func get_admin{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }() -> (admin: felt):
        let (admin) = Proxy_admin.read()
        return (admin)
    end

    #
    # Unprotected
    #

    func _set_admin{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }(new_admin: felt):
        let (previous_admin) = get_admin()
        Proxy_admin.write(new_admin)
        AdminChanged.emit(previous_admin, new_admin)
        return ()
    end

    #
    # Upgrade
    #

    # added for testing purposes
    @external
    func _set_implementation_hash{
            syscall_ptr: felt*,
            pedersen_ptr: HashBuiltin*,
            range_check_ptr
        }(new_implementation: felt):
        with_attr error_message("Proxy: implementation hash cannot be zero"):
            assert_not_zero(new_implementation)
        end

        Proxy_implementation_hash.write(new_implementation)
        Upgraded.emit(new_implementation)
        return ()
    end

end