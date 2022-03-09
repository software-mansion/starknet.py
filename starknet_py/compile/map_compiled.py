# pylint: skip-file
MAP_COMPILED = r"""
{
    "abi": [
        {
            "inputs": [
                {
                    "name": "key",
                    "type": "felt"
                },
                {
                    "name": "value",
                    "type": "felt"
                }
            ],
            "name": "put",
            "outputs": [],
            "type": "function"
        }
    ],
    "entry_points_by_type": {
        "CONSTRUCTOR": [],
        "EXTERNAL": [
            {
                "offset": "0x4",
                "selector": "0x1d7377b4b2053672e38039a02d909f73c4e538c9fddbb7e97aadf700cb9a01a"
            }
        ],
        "L1_HANDLER": []
    },
    "program": {
        "attributes": [],
        "builtins": [
            "pedersen",
            "range_check"
        ],
        "data": [
            "0x480a7ff97fff8000",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x2",
            "0x402a7ffd7ffc7fff",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x480280017ffd8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffff5",
            "0x40780017fff7fff",
            "0x1",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x480680017fff8000",
            "0x0",
            "0x48127ffb7fff8000",
            "0x208b7fff7fff7ffe"
        ],
        "debug_info": {
            "file_contents": {
                "autogen/starknet/arg_processor/1b562308a65653425ce06491fa4b4539466f3251a07e73e099d0afe86a48900e.cairo": "assert [cast(fp + (-4), felt*)] = __calldata_actual_size\n",
                "autogen/starknet/arg_processor/5e1cc73f0b484f90bb02da164d88332b40c6f698801aa4d3c603dab22157e902.cairo": "let __calldata_actual_size =  __calldata_ptr - cast([cast(fp + (-3), felt**)], felt*)\n",
                "autogen/starknet/arg_processor/e27265bcd6d708d2d6657937229a05830427dd5dbf3dc77ae26b6cf2dc04681d.cairo": "let __calldata_arg_key = [__calldata_ptr]\nlet __calldata_ptr = __calldata_ptr + 1\n",
                "autogen/starknet/arg_processor/fc42d727d94c768e43778d12b1fd9241d795ce55b227b746a3ae311d5894c21a.cairo": "let __calldata_arg_value = [__calldata_ptr]\nlet __calldata_ptr = __calldata_ptr + 1\n",
                "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo": "let ret_struct = __wrapped_func{syscall_ptr=syscall_ptr, pedersen_ptr=pedersen_ptr, range_check_ptr=range_check_ptr}(key=__calldata_arg_key, value=__calldata_arg_value,)\n%{ memory[ap] = segments.add() %}        # Allocate memory for return value.\ntempvar retdata : felt*\nlet retdata_size = 0\n",
                "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo": "return (syscall_ptr,pedersen_ptr,range_check_ptr,retdata_size,retdata)\n",
                "autogen/starknet/external/put/6629798b6d541e54a9dc778ffa54e7ef20b4f98b088671dd5070b7e0b547f0e6.cairo": "let pedersen_ptr = [cast([cast(fp + (-5), felt**)] + 1, felt*)]\n",
                "autogen/starknet/external/put/c7060df96cb0acca1380ae43bf758cab727bfdf73cb5d34a93e24a9742817fda.cairo": "let syscall_ptr = [cast([cast(fp + (-5), felt**)] + 0, felt**)]\n",
                "autogen/starknet/external/put/e651458745e7cd218121c342e0915890767e2f59ddc2e315b8844ad0f47d582e.cairo": "let range_check_ptr = [cast([cast(fp + (-5), felt**)] + 2, felt*)]\n"
            },
            "instruction_locations": {
                "0": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__main__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 0,
                            "offset": 0
                        },
                        "reference_ids": {
                            "__main__.put.key": 0,
                            "__main__.put.pedersen_ptr": 3,
                            "__main__.put.range_check_ptr": 4,
                            "__main__.put.syscall_ptr": 2,
                            "__main__.put.value": 1
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 29,
                        "end_line": 7,
                        "input_file": {
                            "filename": "mock.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 29,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 14,
                                        "end_line": 9,
                                        "input_file": {
                                            "filename": "mock.cairo"
                                        },
                                        "start_col": 5,
                                        "start_line": 9
                                    },
                                    "While trying to retrieve the implicit argument 'syscall_ptr' in:"
                                ],
                                "start_col": 10,
                                "start_line": 7
                            },
                            "While expanding the reference 'syscall_ptr' in:"
                        ],
                        "start_col": 10,
                        "start_line": 7
                    }
                },
                "1": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__main__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 0,
                            "offset": 1
                        },
                        "reference_ids": {
                            "__main__.put.key": 0,
                            "__main__.put.pedersen_ptr": 3,
                            "__main__.put.range_check_ptr": 4,
                            "__main__.put.syscall_ptr": 2,
                            "__main__.put.value": 1
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 43,
                        "end_line": 7,
                        "input_file": {
                            "filename": "mock.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 43,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 14,
                                        "end_line": 9,
                                        "input_file": {
                                            "filename": "mock.cairo"
                                        },
                                        "start_col": 5,
                                        "start_line": 9
                                    },
                                    "While trying to retrieve the implicit argument 'pedersen_ptr' in:"
                                ],
                                "start_col": 31,
                                "start_line": 7
                            },
                            "While expanding the reference 'pedersen_ptr' in:"
                        ],
                        "start_col": 31,
                        "start_line": 7
                    }
                },
                "2": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__main__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 0,
                            "offset": 2
                        },
                        "reference_ids": {
                            "__main__.put.key": 0,
                            "__main__.put.pedersen_ptr": 3,
                            "__main__.put.range_check_ptr": 4,
                            "__main__.put.syscall_ptr": 2,
                            "__main__.put.value": 1
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 60,
                        "end_line": 7,
                        "input_file": {
                            "filename": "mock.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 60,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 14,
                                        "end_line": 9,
                                        "input_file": {
                                            "filename": "mock.cairo"
                                        },
                                        "start_col": 5,
                                        "start_line": 9
                                    },
                                    "While trying to retrieve the implicit argument 'range_check_ptr' in:"
                                ],
                                "start_col": 45,
                                "start_line": 7
                            },
                            "While expanding the reference 'range_check_ptr' in:"
                        ],
                        "start_col": 45,
                        "start_line": 7
                    }
                },
                "3": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__main__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 0,
                            "offset": 3
                        },
                        "reference_ids": {
                            "__main__.put.key": 0,
                            "__main__.put.pedersen_ptr": 3,
                            "__main__.put.range_check_ptr": 4,
                            "__main__.put.syscall_ptr": 2,
                            "__main__.put.value": 1
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 14,
                        "end_line": 9,
                        "input_file": {
                            "filename": "mock.cairo"
                        },
                        "start_col": 5,
                        "start_line": 9
                    }
                },
                "4": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 0
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 40,
                        "end_line": 2,
                        "input_file": {
                            "filename": "autogen/starknet/arg_processor/fc42d727d94c768e43778d12b1fd9241d795ce55b227b746a3ae311d5894c21a.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 33,
                                "end_line": 8,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 45,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/arg_processor/5e1cc73f0b484f90bb02da164d88332b40c6f698801aa4d3c603dab22157e902.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "parent_location": [
                                                    {
                                                        "end_col": 57,
                                                        "end_line": 1,
                                                        "input_file": {
                                                            "filename": "autogen/starknet/arg_processor/1b562308a65653425ce06491fa4b4539466f3251a07e73e099d0afe86a48900e.cairo"
                                                        },
                                                        "parent_location": [
                                                            {
                                                                "end_col": 9,
                                                                "end_line": 7,
                                                                "input_file": {
                                                                    "filename": "mock.cairo"
                                                                },
                                                                "start_col": 6,
                                                                "start_line": 7
                                                            },
                                                            "While handling calldata of"
                                                        ],
                                                        "start_col": 35,
                                                        "start_line": 1
                                                    },
                                                    "While expanding the reference '__calldata_actual_size' in:"
                                                ],
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While handling calldata of"
                                        ],
                                        "start_col": 31,
                                        "start_line": 1
                                    },
                                    "While expanding the reference '__calldata_ptr' in:"
                                ],
                                "start_col": 21,
                                "start_line": 8
                            },
                            "While handling calldata argument 'value'"
                        ],
                        "start_col": 22,
                        "start_line": 2
                    }
                },
                "6": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 1
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 57,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/arg_processor/1b562308a65653425ce06491fa4b4539466f3251a07e73e099d0afe86a48900e.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While handling calldata of"
                        ],
                        "start_col": 1,
                        "start_line": 1
                    }
                },
                "7": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 1
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 64,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/c7060df96cb0acca1380ae43bf758cab727bfdf73cb5d34a93e24a9742817fda.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 29,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 56,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 45,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'syscall_ptr' in:"
                                ],
                                "start_col": 10,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 19,
                        "start_line": 1
                    }
                },
                "8": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 2
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 64,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/6629798b6d541e54a9dc778ffa54e7ef20b4f98b088671dd5070b7e0b547f0e6.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 43,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 83,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 71,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'pedersen_ptr' in:"
                                ],
                                "start_col": 31,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 20,
                        "start_line": 1
                    }
                },
                "9": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 3
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 67,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/e651458745e7cd218121c342e0915890767e2f59ddc2e315b8844ad0f47d582e.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 60,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 116,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 101,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'range_check_ptr' in:"
                                ],
                                "start_col": 45,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 23,
                        "start_line": 1
                    }
                },
                "10": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 4
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 42,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/arg_processor/e27265bcd6d708d2d6657937229a05830427dd5dbf3dc77ae26b6cf2dc04681d.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 19,
                                "end_line": 8,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 140,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 122,
                                        "start_line": 1
                                    },
                                    "While expanding the reference '__calldata_arg_key' in:"
                                ],
                                "start_col": 9,
                                "start_line": 8
                            },
                            "While handling calldata argument 'key'"
                        ],
                        "start_col": 26,
                        "start_line": 1
                    }
                },
                "11": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 5
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 44,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/arg_processor/fc42d727d94c768e43778d12b1fd9241d795ce55b227b746a3ae311d5894c21a.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 33,
                                "end_line": 8,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 168,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 148,
                                        "start_line": 1
                                    },
                                    "While expanding the reference '__calldata_arg_value' in:"
                                ],
                                "start_col": 21,
                                "start_line": 8
                            },
                            "While handling calldata argument 'value'"
                        ],
                        "start_col": 28,
                        "start_line": 1
                    }
                },
                "12": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 6
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 6,
                            "__wrappers__.put.range_check_ptr": 7,
                            "__wrappers__.put.syscall_ptr": 5
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 9,
                        "end_line": 7,
                        "input_file": {
                            "filename": "mock.cairo"
                        },
                        "start_col": 6,
                        "start_line": 7
                    }
                },
                "14": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 11
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [
                        {
                            "location": {
                                "end_col": 34,
                                "end_line": 2,
                                "input_file": {
                                    "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 9,
                                        "end_line": 7,
                                        "input_file": {
                                            "filename": "mock.cairo"
                                        },
                                        "start_col": 6,
                                        "start_line": 7
                                    },
                                    "While constructing the external wrapper for:"
                                ],
                                "start_col": 1,
                                "start_line": 2
                            },
                            "n_prefix_newlines": 0
                        }
                    ],
                    "inst": {
                        "end_col": 24,
                        "end_line": 3,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 1,
                        "start_line": 3
                    }
                },
                "16": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 12
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 56,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 20,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 9,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'syscall_ptr' in:"
                                ],
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 45,
                        "start_line": 1
                    }
                },
                "17": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 13
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 83,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 33,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 21,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'pedersen_ptr' in:"
                                ],
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 71,
                        "start_line": 1
                    }
                },
                "18": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 14
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 116,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 49,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 34,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'range_check_ptr' in:"
                                ],
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 101,
                        "start_line": 1
                    }
                },
                "19": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 15
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 21,
                        "end_line": 4,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 62,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 50,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'retdata_size' in:"
                                ],
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 20,
                        "start_line": 4
                    }
                },
                "21": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 16
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 16,
                        "end_line": 3,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/0728af1799e5bb69abda513327ff64877ac28ec8da3fa1cc5db6eebe29f184a5.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "parent_location": [
                                    {
                                        "end_col": 70,
                                        "end_line": 1,
                                        "input_file": {
                                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                                        },
                                        "parent_location": [
                                            {
                                                "end_col": 9,
                                                "end_line": 7,
                                                "input_file": {
                                                    "filename": "mock.cairo"
                                                },
                                                "start_col": 6,
                                                "start_line": 7
                                            },
                                            "While constructing the external wrapper for:"
                                        ],
                                        "start_col": 63,
                                        "start_line": 1
                                    },
                                    "While expanding the reference 'retdata' in:"
                                ],
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 9,
                        "start_line": 3
                    }
                },
                "22": {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 17
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.retdata": 19,
                            "__wrappers__.put.retdata_size": 20,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    },
                    "hints": [],
                    "inst": {
                        "end_col": 71,
                        "end_line": 1,
                        "input_file": {
                            "filename": "autogen/starknet/external/put/4ba2b119ceb30fe10f4cca3c9d73ef620c0fb5eece91b99a99d71217bba1001c.cairo"
                        },
                        "parent_location": [
                            {
                                "end_col": 9,
                                "end_line": 7,
                                "input_file": {
                                    "filename": "mock.cairo"
                                },
                                "start_col": 6,
                                "start_line": 7
                            },
                            "While constructing the external wrapper for:"
                        ],
                        "start_col": 1,
                        "start_line": 1
                    }
                }
            }
        },
        "hints": {
            "14": [
                {
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.put"
                    ],
                    "code": "memory[ap] = segments.add()",
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "group": 1,
                            "offset": 11
                        },
                        "reference_ids": {
                            "__wrappers__.put.__calldata_actual_size": 13,
                            "__wrappers__.put.__calldata_arg_key": 9,
                            "__wrappers__.put.__calldata_arg_value": 11,
                            "__wrappers__.put.__calldata_ptr": 12,
                            "__wrappers__.put.__temp0": 14,
                            "__wrappers__.put.pedersen_ptr": 16,
                            "__wrappers__.put.range_check_ptr": 17,
                            "__wrappers__.put.ret_struct": 18,
                            "__wrappers__.put.syscall_ptr": 15
                        }
                    }
                }
            ]
        },
        "identifiers": {
            "__main__.MockStruct": {
                "destination": "inner.inner.MockStruct",
                "type": "alias"
            },
            "__main__.put": {
                "decorators": [
                    "external"
                ],
                "pc": 0,
                "type": "function"
            },
            "__main__.put.Args": {
                "full_name": "__main__.put.Args",
                "members": {
                    "key": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "value": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "__main__.put.ImplicitArgs": {
                "full_name": "__main__.put.ImplicitArgs",
                "members": {
                    "pedersen_ptr": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "range_check_ptr": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "syscall_ptr": {
                        "cairo_type": "felt*",
                        "offset": 0
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "__main__.put.Return": {
                "full_name": "__main__.put.Return",
                "members": {},
                "size": 0,
                "type": "struct"
            },
            "__main__.put.SIZEOF_LOCALS": {
                "type": "const",
                "value": 0
            },
            "__main__.put.key": {
                "cairo_type": "felt",
                "full_name": "__main__.put.key",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 0,
                            "offset": 0
                        },
                        "pc": 0,
                        "value": "[cast(fp + (-4), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__main__.put.pedersen_ptr": {
                "cairo_type": "felt",
                "full_name": "__main__.put.pedersen_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 0,
                            "offset": 0
                        },
                        "pc": 0,
                        "value": "[cast(fp + (-6), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__main__.put.range_check_ptr": {
                "cairo_type": "felt",
                "full_name": "__main__.put.range_check_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 0,
                            "offset": 0
                        },
                        "pc": 0,
                        "value": "[cast(fp + (-5), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__main__.put.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "__main__.put.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 0,
                            "offset": 0
                        },
                        "pc": 0,
                        "value": "[cast(fp + (-7), felt**)]"
                    }
                ],
                "type": "reference"
            },
            "__main__.put.value": {
                "cairo_type": "felt",
                "full_name": "__main__.put.value",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 0,
                            "offset": 0
                        },
                        "pc": 0,
                        "value": "[cast(fp + (-3), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put": {
                "decorators": [
                    "external"
                ],
                "pc": 4,
                "type": "function"
            },
            "__wrappers__.put.Args": {
                "full_name": "__wrappers__.put.Args",
                "members": {},
                "size": 0,
                "type": "struct"
            },
            "__wrappers__.put.ImplicitArgs": {
                "full_name": "__wrappers__.put.ImplicitArgs",
                "members": {},
                "size": 0,
                "type": "struct"
            },
            "__wrappers__.put.Return": {
                "full_name": "__wrappers__.put.Return",
                "members": {
                    "pedersen_ptr": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "range_check_ptr": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "retdata": {
                        "cairo_type": "felt*",
                        "offset": 4
                    },
                    "size": {
                        "cairo_type": "felt",
                        "offset": 3
                    },
                    "syscall_ptr": {
                        "cairo_type": "felt*",
                        "offset": 0
                    }
                },
                "size": 5,
                "type": "struct"
            },
            "__wrappers__.put.SIZEOF_LOCALS": {
                "type": "const",
                "value": 0
            },
            "__wrappers__.put.__calldata_actual_size": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.__calldata_actual_size",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "cast([fp + (-3)] + 2 - [fp + (-3)], felt)"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.__calldata_arg_key": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.__calldata_arg_key",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast([fp + (-3)], felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.__calldata_arg_value": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.__calldata_arg_value",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast([fp + (-3)] + 1, felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.__calldata_ptr": {
                "cairo_type": "felt*",
                "full_name": "__wrappers__.put.__calldata_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast(fp + (-3), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "cast([fp + (-3)] + 1, felt*)"
                    },
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "cast([fp + (-3)] + 2, felt*)"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.__temp0": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.__temp0",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 1
                        },
                        "pc": 6,
                        "value": "[cast(ap + (-1), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.__wrapped_func": {
                "destination": "__main__.put",
                "type": "alias"
            },
            "__wrappers__.put.pedersen_ptr": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.pedersen_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast([fp + (-5)] + 1, felt*)]"
                    },
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 11
                        },
                        "pc": 14,
                        "value": "[cast(ap + (-2), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.range_check_ptr": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.range_check_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast([fp + (-5)] + 2, felt*)]"
                    },
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 11
                        },
                        "pc": 14,
                        "value": "[cast(ap + (-1), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.ret_struct": {
                "cairo_type": "__main__.put.Return",
                "full_name": "__wrappers__.put.ret_struct",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 11
                        },
                        "pc": 14,
                        "value": "[cast(ap + 0, __main__.put.Return*)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.retdata": {
                "cairo_type": "felt*",
                "full_name": "__wrappers__.put.retdata",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 12
                        },
                        "pc": 16,
                        "value": "[cast(ap + (-1), felt**)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.retdata_size": {
                "cairo_type": "felt",
                "full_name": "__wrappers__.put.retdata_size",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 12
                        },
                        "pc": 16,
                        "value": "cast(0, felt)"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "__wrappers__.put.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 0
                        },
                        "pc": 4,
                        "value": "[cast([fp + (-5)], felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "group": 1,
                            "offset": 11
                        },
                        "pc": 14,
                        "value": "[cast(ap + (-3), felt**)]"
                    }
                ],
                "type": "reference"
            },
            "__wrappers__.put_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "inner.inner.MockStruct": {
                "full_name": "inner.inner.MockStruct",
                "members": {
                    "x": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.BitwiseBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "members": {
                    "x": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "x_and_y": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "x_or_y": {
                        "cairo_type": "felt",
                        "offset": 4
                    },
                    "x_xor_y": {
                        "cairo_type": "felt",
                        "offset": 3
                    },
                    "y": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 5,
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.EcOpBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.EcOpBuiltin",
                "members": {
                    "m": {
                        "cairo_type": "felt",
                        "offset": 4
                    },
                    "p": {
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint",
                        "offset": 0
                    },
                    "q": {
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint",
                        "offset": 2
                    },
                    "r": {
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint",
                        "offset": 5
                    }
                },
                "size": 7,
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.EcPoint": {
                "destination": "starkware.cairo.common.ec_point.EcPoint",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_builtins.HashBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "members": {
                    "result": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "x": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "y": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.SignatureBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.SignatureBuiltin",
                "members": {
                    "message": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "pub_key": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.cairo.common.dict_access.DictAccess": {
                "full_name": "starkware.cairo.common.dict_access.DictAccess",
                "members": {
                    "key": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "new_value": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "prev_value": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "starkware.cairo.common.ec_point.EcPoint": {
                "full_name": "starkware.cairo.common.ec_point.EcPoint",
                "members": {
                    "x": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "y": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.cairo.common.hash.HashBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "type": "alias"
            },
            "starkware.starknet.common.storage.ADDR_BOUND": {
                "type": "const",
                "value": -106710729501573572985208420194530329073740042555888586719489
            },
            "starkware.starknet.common.storage.MAX_STORAGE_ITEM_SIZE": {
                "type": "const",
                "value": 256
            },
            "starkware.starknet.common.storage.assert_250_bit": {
                "destination": "starkware.cairo.common.math.assert_250_bit",
                "type": "alias"
            },
            "starkware.starknet.common.syscalls.CALL_CONTRACT_SELECTOR": {
                "type": "const",
                "value": 20853273475220472486191784820
            },
            "starkware.starknet.common.syscalls.CallContract": {
                "full_name": "starkware.starknet.common.syscalls.CallContract",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.CallContractRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.CallContractResponse",
                        "offset": 5
                    }
                },
                "size": 7,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.CallContractRequest": {
                "full_name": "starkware.starknet.common.syscalls.CallContractRequest",
                "members": {
                    "calldata": {
                        "cairo_type": "felt*",
                        "offset": 4
                    },
                    "calldata_size": {
                        "cairo_type": "felt",
                        "offset": 3
                    },
                    "contract_address": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "function_selector": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 5,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.CallContractResponse": {
                "full_name": "starkware.starknet.common.syscalls.CallContractResponse",
                "members": {
                    "retdata": {
                        "cairo_type": "felt*",
                        "offset": 1
                    },
                    "retdata_size": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.DELEGATE_CALL_SELECTOR": {
                "type": "const",
                "value": 21167594061783206823196716140
            },
            "starkware.starknet.common.syscalls.DELEGATE_L1_HANDLER_SELECTOR": {
                "type": "const",
                "value": 23274015802972845247556842986379118667122
            },
            "starkware.starknet.common.syscalls.DictAccess": {
                "destination": "starkware.cairo.common.dict_access.DictAccess",
                "type": "alias"
            },
            "starkware.starknet.common.syscalls.EMIT_EVENT_SELECTOR": {
                "type": "const",
                "value": 1280709301550335749748
            },
            "starkware.starknet.common.syscalls.EmitEvent": {
                "full_name": "starkware.starknet.common.syscalls.EmitEvent",
                "members": {
                    "data": {
                        "cairo_type": "felt*",
                        "offset": 4
                    },
                    "data_len": {
                        "cairo_type": "felt",
                        "offset": 3
                    },
                    "keys": {
                        "cairo_type": "felt*",
                        "offset": 2
                    },
                    "keys_len": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 5,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GET_BLOCK_NUMBER_SELECTOR": {
                "type": "const",
                "value": 1448089106835523001438702345020786
            },
            "starkware.starknet.common.syscalls.GET_BLOCK_TIMESTAMP_SELECTOR": {
                "type": "const",
                "value": 24294903732626645868215235778792757751152
            },
            "starkware.starknet.common.syscalls.GET_CALLER_ADDRESS_SELECTOR": {
                "type": "const",
                "value": 94901967781393078444254803017658102643
            },
            "starkware.starknet.common.syscalls.GET_CONTRACT_ADDRESS_SELECTOR": {
                "type": "const",
                "value": 6219495360805491471215297013070624192820083
            },
            "starkware.starknet.common.syscalls.GET_SEQUENCER_ADDRESS_SELECTOR": {
                "type": "const",
                "value": 1592190833581991703053805829594610833820054387
            },
            "starkware.starknet.common.syscalls.GET_TX_INFO_SELECTOR": {
                "type": "const",
                "value": 1317029390204112103023
            },
            "starkware.starknet.common.syscalls.GET_TX_SIGNATURE_SELECTOR": {
                "type": "const",
                "value": 1448089128652340074717162277007973
            },
            "starkware.starknet.common.syscalls.GetBlockNumber": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumber",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockNumberRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockNumberResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockNumberRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumberRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockNumberResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumberResponse",
                "members": {
                    "block_number": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestamp": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestamp",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockTimestampRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockTimestampResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestampRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestampRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestampResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestampResponse",
                "members": {
                    "block_timestamp": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddress",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetCallerAddressRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetCallerAddressResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddressRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddressResponse",
                "members": {
                    "caller_address": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddress",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetContractAddressRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetContractAddressResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddressRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddressResponse",
                "members": {
                    "contract_address": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddress",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetSequencerAddressRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetSequencerAddressResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddressRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddressResponse",
                "members": {
                    "sequencer_address": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfo": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfo",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxInfoRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxInfoResponse",
                        "offset": 1
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfoRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfoRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfoResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfoResponse",
                "members": {
                    "tx_info": {
                        "cairo_type": "starkware.starknet.common.syscalls.TxInfo*",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignature": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignature",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxSignatureRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxSignatureResponse",
                        "offset": 1
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignatureRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignatureRequest",
                "members": {
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignatureResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignatureResponse",
                "members": {
                    "signature": {
                        "cairo_type": "felt*",
                        "offset": 1
                    },
                    "signature_len": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.SEND_MESSAGE_TO_L1_SELECTOR": {
                "type": "const",
                "value": 433017908768303439907196859243777073
            },
            "starkware.starknet.common.syscalls.STORAGE_READ_SELECTOR": {
                "type": "const",
                "value": 100890693370601760042082660
            },
            "starkware.starknet.common.syscalls.STORAGE_WRITE_SELECTOR": {
                "type": "const",
                "value": 25828017502874050592466629733
            },
            "starkware.starknet.common.syscalls.SendMessageToL1SysCall": {
                "full_name": "starkware.starknet.common.syscalls.SendMessageToL1SysCall",
                "members": {
                    "payload_ptr": {
                        "cairo_type": "felt*",
                        "offset": 3
                    },
                    "payload_size": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "to_address": {
                        "cairo_type": "felt",
                        "offset": 1
                    }
                },
                "size": 4,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageRead": {
                "full_name": "starkware.starknet.common.syscalls.StorageRead",
                "members": {
                    "request": {
                        "cairo_type": "starkware.starknet.common.syscalls.StorageReadRequest",
                        "offset": 0
                    },
                    "response": {
                        "cairo_type": "starkware.starknet.common.syscalls.StorageReadResponse",
                        "offset": 2
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageReadRequest": {
                "full_name": "starkware.starknet.common.syscalls.StorageReadRequest",
                "members": {
                    "address": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 2,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageReadResponse": {
                "full_name": "starkware.starknet.common.syscalls.StorageReadResponse",
                "members": {
                    "value": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 1,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageWrite": {
                "full_name": "starkware.starknet.common.syscalls.StorageWrite",
                "members": {
                    "address": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "selector": {
                        "cairo_type": "felt",
                        "offset": 0
                    },
                    "value": {
                        "cairo_type": "felt",
                        "offset": 2
                    }
                },
                "size": 3,
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.TxInfo": {
                "full_name": "starkware.starknet.common.syscalls.TxInfo",
                "members": {
                    "account_contract_address": {
                        "cairo_type": "felt",
                        "offset": 1
                    },
                    "max_fee": {
                        "cairo_type": "felt",
                        "offset": 2
                    },
                    "signature": {
                        "cairo_type": "felt*",
                        "offset": 4
                    },
                    "signature_len": {
                        "cairo_type": "felt",
                        "offset": 3
                    },
                    "version": {
                        "cairo_type": "felt",
                        "offset": 0
                    }
                },
                "size": 5,
                "type": "struct"
            }
        },
        "main_scope": "__main__",
        "prime": "0x800000000000011000000000000000000000000000000000000000000000001",
        "reference_manager": {
            "references": [
                {
                    "ap_tracking_data": {
                        "group": 0,
                        "offset": 0
                    },
                    "pc": 0,
                    "value": "[cast(fp + (-4), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 0,
                        "offset": 0
                    },
                    "pc": 0,
                    "value": "[cast(fp + (-3), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 0,
                        "offset": 0
                    },
                    "pc": 0,
                    "value": "[cast(fp + (-7), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 0,
                        "offset": 0
                    },
                    "pc": 0,
                    "value": "[cast(fp + (-6), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 0,
                        "offset": 0
                    },
                    "pc": 0,
                    "value": "[cast(fp + (-5), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast([fp + (-5)], felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast([fp + (-5)] + 1, felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast([fp + (-5)] + 2, felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast(fp + (-3), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast([fp + (-3)], felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "cast([fp + (-3)] + 1, felt*)"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "[cast([fp + (-3)] + 1, felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "cast([fp + (-3)] + 2, felt*)"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 0
                    },
                    "pc": 4,
                    "value": "cast([fp + (-3)] + 2 - [fp + (-3)], felt)"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 1
                    },
                    "pc": 6,
                    "value": "[cast(ap + (-1), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 11
                    },
                    "pc": 14,
                    "value": "[cast(ap + (-3), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 11
                    },
                    "pc": 14,
                    "value": "[cast(ap + (-2), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 11
                    },
                    "pc": 14,
                    "value": "[cast(ap + (-1), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 11
                    },
                    "pc": 14,
                    "value": "[cast(ap + 0, __main__.put.Return*)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 12
                    },
                    "pc": 16,
                    "value": "[cast(ap + (-1), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "group": 1,
                        "offset": 12
                    },
                    "pc": 16,
                    "value": "cast(0, felt)"
                }
            ]
        }
    }
}

"""
