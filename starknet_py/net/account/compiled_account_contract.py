# pylint: disable=too-many-lines
COMPILED_ACCOUNT_CONTRACT = r"""
{
    "entry_points_by_type": {
        "CONSTRUCTOR": [
            {
                "selector": "0x28ffe4ff0f226a9107253e17a904099aa4f63a02a5621de0576e5aa71bc5194",
                "offset": "0x121"
            }
        ],
        "EXTERNAL": [
            {
                "selector": "0xbc0eb87884ab91e330445c3584a50d7ddf4b568f02fbeb456a6242cce3f5d9",
                "offset": "0x180"
            },
            {
                "selector": "0x15d40a3d6ca2ac30f4031e42be28da9b056fef9bb7357ac5e85627ee876e5ad",
                "offset": "0x246"
            },
            {
                "selector": "0x162da33a4585851fe8d3af3c2a9c60b557814e221e0d4f30ff0b2189d9c7775",
                "offset": "0x1d7"
            },
            {
                "selector": "0x1a6c6a0bdec86cc645c91997d8eea83e87148659e3e61122f72361fd5e94079",
                "offset": "0x144"
            },
            {
                "selector": "0x213dfe25e2ca309c4d615a09cfc95fdb2fc7dc73fbcad12c450fe93b1f2ff9e",
                "offset": "0x1a7"
            },
            {
                "selector": "0x289da278a8dc833409cabfdad1581e8e7d40e42dcaed693fa4008dcdb4963b3",
                "offset": "0x212"
            },
            {
                "selector": "0x29e211664c0b63c79638fbea474206ca74016b3e9a3dc4f9ac300ffd8bdf2cd",
                "offset": "0x165"
            }
        ],
        "L1_HANDLER": []
    },
    "abi": [
        {
            "members": [
                {
                    "name": "to",
                    "offset": 0,
                    "type": "felt"
                },
                {
                    "name": "selector",
                    "offset": 1,
                    "type": "felt"
                },
                {
                    "name": "data_offset",
                    "offset": 2,
                    "type": "felt"
                },
                {
                    "name": "data_len",
                    "offset": 3,
                    "type": "felt"
                }
            ],
            "name": "AccountCallArray",
            "size": 4,
            "type": "struct"
        },
        {
            "inputs": [
                {
                    "name": "public_key",
                    "type": "felt"
                }
            ],
            "name": "constructor",
            "outputs": [],
            "type": "constructor"
        },
        {
            "inputs": [],
            "name": "getPublicKey",
            "outputs": [
                {
                    "name": "publicKey",
                    "type": "felt"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "interfaceId",
                    "type": "felt"
                }
            ],
            "name": "supportsInterface",
            "outputs": [
                {
                    "name": "success",
                    "type": "felt"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "newPublicKey",
                    "type": "felt"
                }
            ],
            "name": "setPublicKey",
            "outputs": [],
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "hash",
                    "type": "felt"
                },
                {
                    "name": "signature_len",
                    "type": "felt"
                },
                {
                    "name": "signature",
                    "type": "felt*"
                }
            ],
            "name": "isValidSignature",
            "outputs": [
                {
                    "name": "isValid",
                    "type": "felt"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "call_array_len",
                    "type": "felt"
                },
                {
                    "name": "call_array",
                    "type": "AccountCallArray*"
                },
                {
                    "name": "calldata_len",
                    "type": "felt"
                },
                {
                    "name": "calldata",
                    "type": "felt*"
                }
            ],
            "name": "__validate__",
            "outputs": [],
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "class_hash",
                    "type": "felt"
                }
            ],
            "name": "__validate_declare__",
            "outputs": [],
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "call_array_len",
                    "type": "felt"
                },
                {
                    "name": "call_array",
                    "type": "AccountCallArray*"
                },
                {
                    "name": "calldata_len",
                    "type": "felt"
                },
                {
                    "name": "calldata",
                    "type": "felt*"
                }
            ],
            "name": "__execute__",
            "outputs": [
                {
                    "name": "response_len",
                    "type": "felt"
                },
                {
                    "name": "response",
                    "type": "felt*"
                }
            ],
            "type": "function"
        }
    ],
    "program": {
        "data": [
            "0x40780017fff7fff",
            "0x1",
            "0x208b7fff7fff7ffe",
            "0x20780017fff7ffd",
            "0x3",
            "0x208b7fff7fff7ffe",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480080007fff8000",
            "0x400080007ffd7fff",
            "0x482480017ffd8001",
            "0x1",
            "0x482480017ffd8001",
            "0x1",
            "0xa0680017fff7ffe",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffffb",
            "0x402a7ffc7ffd7fff",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x43616c6c436f6e7472616374",
            "0x400280007ff97fff",
            "0x400380017ff97ffa",
            "0x400380027ff97ffb",
            "0x400380037ff97ffc",
            "0x400380047ff97ffd",
            "0x482680017ff98000",
            "0x7",
            "0x480280057ff98000",
            "0x480280067ff98000",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x47657443616c6c657241646472657373",
            "0x400280007ffd7fff",
            "0x482680017ffd8000",
            "0x2",
            "0x480280017ffd8000",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x476574436f6e747261637441646472657373",
            "0x400280007ffd7fff",
            "0x482680017ffd8000",
            "0x2",
            "0x480280017ffd8000",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x53746f7261676552656164",
            "0x400280007ffc7fff",
            "0x400380017ffc7ffd",
            "0x482680017ffc8000",
            "0x3",
            "0x480280027ffc8000",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x53746f726167655772697465",
            "0x400280007ffb7fff",
            "0x400380017ffb7ffc",
            "0x400380027ffb7ffd",
            "0x482680017ffb8000",
            "0x3",
            "0x208b7fff7fff7ffe",
            "0x480680017fff8000",
            "0x4765745478496e666f",
            "0x400280007ffd7fff",
            "0x482680017ffd8000",
            "0x2",
            "0x480280017ffd8000",
            "0x208b7fff7fff7ffe",
            "0x400380017ff97ffa",
            "0x400380007ff97ffb",
            "0x482680017ff98000",
            "0x2",
            "0x208b7fff7fff7ffe",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x480680017fff8000",
            "0x1379ac0624b939ceb9dede92211d7db5ee174fe28be72245b0a1a2abd81c98f",
            "0x208b7fff7fff7ffe",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffffa",
            "0x480a7ffb7fff8000",
            "0x48127ffe7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffda",
            "0x48127ffe7fff8000",
            "0x48127ff57fff8000",
            "0x48127ff57fff8000",
            "0x48127ffc7fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffed",
            "0x480a7ffa7fff8000",
            "0x48127ffe7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffd4",
            "0x48127ff67fff8000",
            "0x48127ff67fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffff1",
            "0x208b7fff7fff7ffe",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffb8",
            "0x48127ffe7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffae",
            "0x40127fff7fff7ff9",
            "0x48127ffe7fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffd5",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffe00365a",
            "0x20680017fff7fff",
            "0x8",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480680017fff8000",
            "0x1",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffff59942a8c",
            "0x20680017fff7fff",
            "0x8",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480680017fff8000",
            "0x1",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480680017fff8000",
            "0x0",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffd7",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffbf",
            "0x208b7fff7fff7ffe",
            "0x480a7ff77fff8000",
            "0x480a7ff87fff8000",
            "0x480a7ffa7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffac",
            "0x480a7ff97fff8000",
            "0x480a7ffb7fff8000",
            "0x48127ffd7fff8000",
            "0x480280007ffd8000",
            "0x480280017ffd8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff9b",
            "0x48127ff47fff8000",
            "0x48127ff47fff8000",
            "0x48127ffd7fff8000",
            "0x48127ff37fff8000",
            "0x480680017fff8000",
            "0x1",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x2",
            "0x480a7ff57fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff88",
            "0x480080007fff8000",
            "0x482480017fff8000",
            "0x800000000000011000000000000000000000000000000000000000000000000",
            "0x480080007ffd8000",
            "0x482480017fff8000",
            "0x800000000000010ffffffffffffffff00000000000000000000000000000000",
            "0x480680017fff8000",
            "0x0",
            "0x40507ffe7ffc7fff",
            "0x48127ff97fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff5e",
            "0x400680017fff7fff",
            "0x0",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff3c",
            "0x40137fff7fff8000",
            "0x48127ffb7fff8000",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffd7fff8000",
            "0x480a80007fff8000",
            "0x1104800180018000",
            "0x35",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff32",
            "0x40137fff7fff8001",
            "0x48127ffc7fff8000",
            "0x480a7ffa7fff8000",
            "0x480a80007fff8000",
            "0x480a80017fff8000",
            "0x1104800180018000",
            "0xa",
            "0x48127ffe7fff8000",
            "0x480a7ff67fff8000",
            "0x480a7ff77fff8000",
            "0x480a7ff87fff8000",
            "0x480a7ff97fff8000",
            "0x48127ffa7fff8000",
            "0x480a80017fff8000",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x3",
            "0x20780017fff7ffb",
            "0x6",
            "0x480a7ffa7fff8000",
            "0x480680017fff8000",
            "0x0",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480280007ffc8000",
            "0x480280017ffc8000",
            "0x480280027ffc8000",
            "0x480280037ffc8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff26",
            "0x40137ffe7fff8000",
            "0x40137fff7fff8001",
            "0x40137ffd7fff8002",
            "0x480a7ffd7fff8000",
            "0x480a80017fff8000",
            "0x480a80007fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff0f",
            "0x480a80027fff8000",
            "0x482680017ffb8000",
            "0x800000000000011000000000000000000000000000000000000000000000000",
            "0x482680017ffc8000",
            "0x4",
            "0x482a80007ffd8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffe4",
            "0x48127ffe7fff8000",
            "0x482880007ffe8000",
            "0x208b7fff7fff7ffe",
            "0x20780017fff7ffa",
            "0x4",
            "0x480a7ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480280007ffb8000",
            "0x400280007ffd7fff",
            "0x480280017ffb8000",
            "0x400280017ffd7fff",
            "0x480280037ffb8000",
            "0x400280027ffd7fff",
            "0x480280027ffb8000",
            "0x48327fff7ffc8000",
            "0x400280037ffd7fff",
            "0x480a7ff97fff8000",
            "0x482680017ffa8000",
            "0x800000000000011000000000000000000000000000000000000000000000000",
            "0x482680017ffb8000",
            "0x4",
            "0x480a7ffc7fff8000",
            "0x482680017ffd8000",
            "0x4",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffec",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff49",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x1",
            "0x402a7ffd7ffc7fff",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffff3",
            "0x40780017fff7fff",
            "0x1",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x480280037ffb8000",
            "0x480280047ffb8000",
            "0x480680017fff8000",
            "0x0",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff3f",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x1",
            "0x4003800080007ffc",
            "0x4826800180008000",
            "0x1",
            "0x480a7ffd7fff8000",
            "0x4828800080007ffe",
            "0x480a80007fff8000",
            "0x208b7fff7fff7ffe",
            "0x402b7ffd7ffc7ffd",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280027ffb8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffee",
            "0x48127ffe7fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffff1",
            "0x48127ff47fff8000",
            "0x48127ff47fff8000",
            "0x48127ffb7fff8000",
            "0x480280037ffb8000",
            "0x480280047ffb8000",
            "0x48127ff97fff8000",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff24",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x1",
            "0x4003800080007ffc",
            "0x4826800180008000",
            "0x1",
            "0x480a7ffd7fff8000",
            "0x4828800080007ffe",
            "0x480a80007fff8000",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x1",
            "0x402a7ffd7ffc7fff",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffea",
            "0x48127ffe7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffee",
            "0x48127ff47fff8000",
            "0x48127ff47fff8000",
            "0x48127ffb7fff8000",
            "0x480280037ffb8000",
            "0x480280047ffb8000",
            "0x48127ff97fff8000",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff1a",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x1",
            "0x402a7ffd7ffc7fff",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffff3",
            "0x40780017fff7fff",
            "0x1",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x48127ffc7fff8000",
            "0x480280037ffb8000",
            "0x480280047ffb8000",
            "0x480680017fff8000",
            "0x0",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ff77fff8000",
            "0x480a7ff87fff8000",
            "0x480a7ff97fff8000",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffff05",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x1",
            "0x4003800080007ffc",
            "0x4826800180008000",
            "0x1",
            "0x480a7ffd7fff8000",
            "0x4828800080007ffe",
            "0x480a80007fff8000",
            "0x208b7fff7fff7ffe",
            "0x480280027ffb8000",
            "0x480280017ffd8000",
            "0x400080007ffe7fff",
            "0x482680017ffd8000",
            "0x2",
            "0x480280017ffd8000",
            "0x48307fff7ffe8000",
            "0x402a7ffd7ffc7fff",
            "0x480280027ffb8000",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280037ffb8000",
            "0x482480017ffc8000",
            "0x1",
            "0x480280007ffd8000",
            "0x480280017ffd8000",
            "0x482680017ffd8000",
            "0x2",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffdc",
            "0x48127ffe7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffe3",
            "0x48127ff37fff8000",
            "0x48127ff37fff8000",
            "0x48127ffb7fff8000",
            "0x48127ff27fff8000",
            "0x480280047ffb8000",
            "0x48127ff97fff8000",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ff67fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffe76",
            "0x48127ffe7fff8000",
            "0x480a7ff77fff8000",
            "0x480a7ff87fff8000",
            "0x480a7ff97fff8000",
            "0x480080057ffb8000",
            "0x480080037ffa8000",
            "0x480080047ff98000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffed0",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x208b7fff7fff7ffe",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x400080007ffe7fff",
            "0x482680017ffd8000",
            "0x1",
            "0x480280007ffd8000",
            "0x484480017fff8000",
            "0x4",
            "0x48307fff7ffd8000",
            "0x480280027ffb8000",
            "0x480080007ffe8000",
            "0x400080017ffe7fff",
            "0x482480017ffd8000",
            "0x1",
            "0x480080007ffc8000",
            "0x48307fff7ffe8000",
            "0x402a7ffd7ffc7fff",
            "0x480280027ffb8000",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280037ffb8000",
            "0x482480017ffc8000",
            "0x2",
            "0x480280007ffd8000",
            "0x482680017ffd8000",
            "0x1",
            "0x480080007ff38000",
            "0x482480017ff28000",
            "0x1",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffd3",
            "0x40780017fff7fff",
            "0x1",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffc7fff8000",
            "0x48127ffa7fff8000",
            "0x480280047ffb8000",
            "0x480680017fff8000",
            "0x0",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ff97fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffe3b",
            "0x48127ffe7fff8000",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480080057ffb8000",
            "0x480080037ffa8000",
            "0x480080047ff98000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffe95",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x208b7fff7fff7ffe",
            "0x482680017ffd8000",
            "0x1",
            "0x402a7ffd7ffc7fff",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280037ffb8000",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffe8",
            "0x40780017fff7fff",
            "0x1",
            "0x48127ffb7fff8000",
            "0x48127ffb7fff8000",
            "0x48127ffc7fff8000",
            "0x48127ffa7fff8000",
            "0x480280047ffb8000",
            "0x480680017fff8000",
            "0x0",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe",
            "0x480a7ff57fff8000",
            "0x480a7ff67fff8000",
            "0x480a7ff77fff8000",
            "0x480a7ff87fff8000",
            "0x480a7ff97fff8000",
            "0x480a7ffa7fff8000",
            "0x480a7ffb7fff8000",
            "0x480a7ffc7fff8000",
            "0x480a7ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffe83",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x3",
            "0x4003800080007ffb",
            "0x400380007ffd7ffb",
            "0x402780017ffd8001",
            "0x1",
            "0x4826800180008000",
            "0x1",
            "0x40297ffb7fff8002",
            "0x4826800180008000",
            "0x1",
            "0x480a7ffc7fff8000",
            "0x480a7ffb7fff8000",
            "0x1104800180018000",
            "0x800000000000010fffffffffffffffffffffffffffffffffffffffffffffdc4",
            "0x480a80017fff8000",
            "0x4829800080008002",
            "0x480a80007fff8000",
            "0x208b7fff7fff7ffe",
            "0x40780017fff7fff",
            "0x4",
            "0x480280027ffb8000",
            "0x480280007ffd8000",
            "0x400080007ffe7fff",
            "0x482680017ffd8000",
            "0x1",
            "0x480280007ffd8000",
            "0x484480017fff8000",
            "0x4",
            "0x48307fff7ffd8000",
            "0x480280027ffb8000",
            "0x480080007ffe8000",
            "0x400080017ffe7fff",
            "0x482480017ffd8000",
            "0x1",
            "0x480080007ffc8000",
            "0x48307fff7ffe8000",
            "0x402a7ffd7ffc7fff",
            "0x480280027ffb8000",
            "0x480280007ffb8000",
            "0x480280017ffb8000",
            "0x480280037ffb8000",
            "0x480280047ffb8000",
            "0x482480017ffb8000",
            "0x2",
            "0x480280007ffd8000",
            "0x482680017ffd8000",
            "0x1",
            "0x480080007ff28000",
            "0x482480017ff18000",
            "0x1",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffc2",
            "0x40137ff97fff8000",
            "0x40137ffa7fff8001",
            "0x40137ffb7fff8002",
            "0x40137ffc7fff8003",
            "0x48127ffd7fff8000",
            "0x1104800180018000",
            "0x800000000000010ffffffffffffffffffffffffffffffffffffffffffffffc7",
            "0x480a80007fff8000",
            "0x480a80017fff8000",
            "0x48127ffb7fff8000",
            "0x480a80027fff8000",
            "0x480a80037fff8000",
            "0x48127ff97fff8000",
            "0x48127ff97fff8000",
            "0x208b7fff7fff7ffe"
        ],
        "attributes": [
            {
                "end_pc": 116,
                "accessible_scopes": [
                    "openzeppelin.account.library",
                    "openzeppelin.account.library.Account",
                    "openzeppelin.account.library.Account.assert_only_self"
                ],
                "flow_tracking_data": {
                    "ap_tracking": {
                        "offset": 12,
                        "group": 13
                    },
                    "reference_ids": {}
                },
                "name": "error_message",
                "start_pc": 115,
                "value": "Account: caller is not this account"
            },
            {
                "end_pc": 192,
                "accessible_scopes": [
                    "openzeppelin.account.library",
                    "openzeppelin.account.library.Account",
                    "openzeppelin.account.library.Account.execute"
                ],
                "flow_tracking_data": {
                    "ap_tracking": {
                        "offset": 8,
                        "group": 18
                    },
                    "reference_ids": {}
                },
                "name": "error_message",
                "start_pc": 183,
                "value": "Account: invalid tx version"
            },
            {
                "end_pc": 197,
                "accessible_scopes": [
                    "openzeppelin.account.library",
                    "openzeppelin.account.library.Account",
                    "openzeppelin.account.library.Account.execute"
                ],
                "flow_tracking_data": {
                    "ap_tracking": {
                        "offset": 19,
                        "group": 18
                    },
                    "reference_ids": {}
                },
                "name": "error_message",
                "start_pc": 195,
                "value": "Account: no reentrant call"
            }
        ],
        "hints": {
            "0": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 0
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "starkware.cairo.common.alloc",
                        "starkware.cairo.common.alloc.alloc"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "6": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 1
                        },
                        "reference_ids": {
                            "starkware.cairo.common.memcpy.memcpy.len": 0
                        }
                    },
                    "accessible_scopes": [
                        "starkware.cairo.common.memcpy",
                        "starkware.cairo.common.memcpy.memcpy"
                    ],
                    "code": "vm_enter_scope({'n': ids.len})"
                }
            ],
            "14": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 5,
                            "group": 1
                        },
                        "reference_ids": {
                            "starkware.cairo.common.memcpy.memcpy.continue_copying": 1
                        }
                    },
                    "accessible_scopes": [
                        "starkware.cairo.common.memcpy",
                        "starkware.cairo.common.memcpy.memcpy"
                    ],
                    "code": "n -= 1\nids.continue_copying = 1 if n > 0 else 0"
                }
            ],
            "17": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 6,
                            "group": 1
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "starkware.cairo.common.memcpy",
                        "starkware.cairo.common.memcpy.memcpy"
                    ],
                    "code": "vm_exit_scope()"
                }
            ],
            "25": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 2
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.call_contract.syscall_ptr": 2
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.call_contract"
                    ],
                    "code": "syscall_handler.call_contract(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "33": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 3
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.get_caller_address.syscall_ptr": 3
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.get_caller_address"
                    ],
                    "code": "syscall_handler.get_caller_address(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "40": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 4
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.get_contract_address.syscall_ptr": 4
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.get_contract_address"
                    ],
                    "code": "syscall_handler.get_contract_address(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "48": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 5
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.storage_read.syscall_ptr": 5
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.storage_read"
                    ],
                    "code": "syscall_handler.storage_read(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "57": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 6
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.storage_write.syscall_ptr": 6
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.storage_write"
                    ],
                    "code": "syscall_handler.storage_write(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "63": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 1,
                            "group": 7
                        },
                        "reference_ids": {
                            "starkware.starknet.common.syscalls.get_tx_info.syscall_ptr": 7
                        }
                    },
                    "accessible_scopes": [
                        "starkware.starknet.common.syscalls",
                        "starkware.starknet.common.syscalls.get_tx_info"
                    ],
                    "code": "syscall_handler.get_tx_info(segments=segments, syscall_ptr=ids.syscall_ptr)"
                }
            ],
            "67": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 8
                        },
                        "reference_ids": {
                            "starkware.cairo.common.signature.verify_ecdsa_signature.ecdsa_ptr": 10,
                            "starkware.cairo.common.signature.verify_ecdsa_signature.signature_r": 8,
                            "starkware.cairo.common.signature.verify_ecdsa_signature.signature_s": 9
                        }
                    },
                    "accessible_scopes": [
                        "starkware.cairo.common.signature",
                        "starkware.cairo.common.signature.verify_ecdsa_signature"
                    ],
                    "code": "ecdsa_builtin.add_signature(ids.ecdsa_ptr.address_, (ids.signature_r, ids.signature_s))"
                }
            ],
            "298": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 35,
                            "group": 27
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.constructor"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "315": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 29
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.getPublicKey_encode_return"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "348": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 33
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.supportsInterface_encode_return"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "393": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 50,
                            "group": 37
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.setPublicKey"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "414": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 39
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.isValidSignature_encode_return"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "502": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 77,
                            "group": 42
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.__validate__"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "540": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 63,
                            "group": 44
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.__validate_declare__"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ],
            "563": [
                {
                    "flow_tracking_data": {
                        "ap_tracking": {
                            "offset": 0,
                            "group": 47
                        },
                        "reference_ids": {}
                    },
                    "accessible_scopes": [
                        "__main__",
                        "__main__",
                        "__wrappers__",
                        "__wrappers__.__execute___encode_return"
                    ],
                    "code": "memory[ap] = segments.add()"
                }
            ]
        },
        "identifiers": {
            "__main__.Account": {
                "destination": "openzeppelin.account.library.Account",
                "type": "alias"
            },
            "__main__.AccountCallArray": {
                "destination": "openzeppelin.account.library.AccountCallArray",
                "type": "alias"
            },
            "__main__.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "__main__.HashBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "type": "alias"
            },
            "__main__.SignatureBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.SignatureBuiltin",
                "type": "alias"
            },
            "__main__.__execute__": {
                "decorators": [
                    "external"
                ],
                "pc": 551,
                "type": "function"
            },
            "__main__.__execute__.Args": {
                "full_name": "__main__.__execute__.Args",
                "size": 4,
                "members": {
                    "call_array_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "call_array": {
                        "offset": 1,
                        "cairo_type": "openzeppelin.account.library.AccountCallArray*"
                    },
                    "calldata_len": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "__main__.__execute__.ImplicitArgs": {
                "full_name": "__main__.__execute__.ImplicitArgs",
                "size": 5,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "bitwise_ptr": {
                        "offset": 3,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 4,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.__execute__.Return": {
                "cairo_type": "(response_len: felt, response: felt*)",
                "type": "type_definition"
            },
            "__main__.__execute__.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.__validate__": {
                "decorators": [
                    "external"
                ],
                "pc": 454,
                "type": "function"
            },
            "__main__.__validate__.Args": {
                "full_name": "__main__.__validate__.Args",
                "size": 4,
                "members": {
                    "call_array_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "call_array": {
                        "offset": 1,
                        "cairo_type": "openzeppelin.account.library.AccountCallArray*"
                    },
                    "calldata_len": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "__main__.__validate__.ImplicitArgs": {
                "full_name": "__main__.__validate__.ImplicitArgs",
                "size": 4,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.__validate__.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "__main__.__validate__.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.__validate_declare__": {
                "decorators": [
                    "external"
                ],
                "pc": 513,
                "type": "function"
            },
            "__main__.__validate_declare__.Args": {
                "full_name": "__main__.__validate_declare__.Args",
                "size": 1,
                "members": {
                    "class_hash": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.__validate_declare__.ImplicitArgs": {
                "full_name": "__main__.__validate_declare__.ImplicitArgs",
                "size": 4,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.__validate_declare__.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "__main__.__validate_declare__.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.constructor": {
                "decorators": [
                    "constructor"
                ],
                "pc": 282,
                "type": "function"
            },
            "__main__.constructor.Args": {
                "full_name": "__main__.constructor.Args",
                "size": 1,
                "members": {
                    "public_key": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.constructor.ImplicitArgs": {
                "full_name": "__main__.constructor.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.constructor.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "__main__.constructor.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.getPublicKey": {
                "decorators": [
                    "view"
                ],
                "pc": 309,
                "type": "function"
            },
            "__main__.getPublicKey.Args": {
                "full_name": "__main__.getPublicKey.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__main__.getPublicKey.ImplicitArgs": {
                "full_name": "__main__.getPublicKey.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.getPublicKey.Return": {
                "cairo_type": "(publicKey: felt)",
                "type": "type_definition"
            },
            "__main__.getPublicKey.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.get_tx_info": {
                "destination": "starkware.starknet.common.syscalls.get_tx_info",
                "type": "alias"
            },
            "__main__.isValidSignature": {
                "decorators": [
                    "view"
                ],
                "pc": 404,
                "type": "function"
            },
            "__main__.isValidSignature.Args": {
                "full_name": "__main__.isValidSignature.Args",
                "size": 3,
                "members": {
                    "hash": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "signature_len": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "signature": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "__main__.isValidSignature.ImplicitArgs": {
                "full_name": "__main__.isValidSignature.ImplicitArgs",
                "size": 4,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.isValidSignature.Return": {
                "cairo_type": "(isValid: felt)",
                "type": "type_definition"
            },
            "__main__.isValidSignature.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.setPublicKey": {
                "decorators": [
                    "external"
                ],
                "pc": 377,
                "type": "function"
            },
            "__main__.setPublicKey.Args": {
                "full_name": "__main__.setPublicKey.Args",
                "size": 1,
                "members": {
                    "newPublicKey": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.setPublicKey.ImplicitArgs": {
                "full_name": "__main__.setPublicKey.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.setPublicKey.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "__main__.setPublicKey.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__main__.supportsInterface": {
                "decorators": [
                    "view"
                ],
                "pc": 341,
                "type": "function"
            },
            "__main__.supportsInterface.Args": {
                "full_name": "__main__.supportsInterface.Args",
                "size": 1,
                "members": {
                    "interfaceId": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.supportsInterface.ImplicitArgs": {
                "full_name": "__main__.supportsInterface.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__main__.supportsInterface.Return": {
                "cairo_type": "(success: felt)",
                "type": "type_definition"
            },
            "__main__.supportsInterface.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.__execute__": {
                "decorators": [
                    "external"
                ],
                "pc": 582,
                "type": "function"
            },
            "__wrappers__.__execute__.Args": {
                "full_name": "__wrappers__.__execute__.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__execute__.ImplicitArgs": {
                "full_name": "__wrappers__.__execute__.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__execute__.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: starkware.cairo.common.cairo_builtins.SignatureBuiltin*, bitwise_ptr: starkware.cairo.common.cairo_builtins.BitwiseBuiltin*, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.__execute__.SIZEOF_LOCALS": {
                "value": 4,
                "type": "const"
            },
            "__wrappers__.__execute__.__wrapped_func": {
                "destination": "__main__.__execute__",
                "type": "alias"
            },
            "__wrappers__.__execute___encode_return": {
                "decorators": [],
                "pc": 563,
                "type": "function"
            },
            "__wrappers__.__execute___encode_return.Args": {
                "full_name": "__wrappers__.__execute___encode_return.Args",
                "size": 3,
                "members": {
                    "ret_value": {
                        "offset": 0,
                        "cairo_type": "(response_len: felt, response: felt*)"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__wrappers__.__execute___encode_return.ImplicitArgs": {
                "full_name": "__wrappers__.__execute___encode_return.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__execute___encode_return.Return": {
                "cairo_type": "(range_check_ptr: felt, data_len: felt, data: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.__execute___encode_return.SIZEOF_LOCALS": {
                "value": 3,
                "type": "const"
            },
            "__wrappers__.__execute___encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.__validate__": {
                "decorators": [
                    "external"
                ],
                "pc": 471,
                "type": "function"
            },
            "__wrappers__.__validate__.Args": {
                "full_name": "__wrappers__.__validate__.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__validate__.ImplicitArgs": {
                "full_name": "__wrappers__.__validate__.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__validate__.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: starkware.cairo.common.cairo_builtins.SignatureBuiltin*, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.__validate__.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.__validate__.__wrapped_func": {
                "destination": "__main__.__validate__",
                "type": "alias"
            },
            "__wrappers__.__validate___encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.__validate_declare__": {
                "decorators": [
                    "external"
                ],
                "pc": 530,
                "type": "function"
            },
            "__wrappers__.__validate_declare__.Args": {
                "full_name": "__wrappers__.__validate_declare__.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__validate_declare__.ImplicitArgs": {
                "full_name": "__wrappers__.__validate_declare__.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.__validate_declare__.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: starkware.cairo.common.cairo_builtins.SignatureBuiltin*, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.__validate_declare__.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.__validate_declare__.__wrapped_func": {
                "destination": "__main__.__validate_declare__",
                "type": "alias"
            },
            "__wrappers__.__validate_declare___encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.constructor": {
                "decorators": [
                    "constructor"
                ],
                "pc": 289,
                "type": "function"
            },
            "__wrappers__.constructor.Args": {
                "full_name": "__wrappers__.constructor.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.constructor.ImplicitArgs": {
                "full_name": "__wrappers__.constructor.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.constructor.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: felt, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.constructor.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.constructor.__wrapped_func": {
                "destination": "__main__.constructor",
                "type": "alias"
            },
            "__wrappers__.constructor_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.getPublicKey": {
                "decorators": [
                    "view"
                ],
                "pc": 324,
                "type": "function"
            },
            "__wrappers__.getPublicKey.Args": {
                "full_name": "__wrappers__.getPublicKey.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.getPublicKey.ImplicitArgs": {
                "full_name": "__wrappers__.getPublicKey.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.getPublicKey.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: felt, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.getPublicKey.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.getPublicKey.__wrapped_func": {
                "destination": "__main__.getPublicKey",
                "type": "alias"
            },
            "__wrappers__.getPublicKey_encode_return": {
                "decorators": [],
                "pc": 315,
                "type": "function"
            },
            "__wrappers__.getPublicKey_encode_return.Args": {
                "full_name": "__wrappers__.getPublicKey_encode_return.Args",
                "size": 2,
                "members": {
                    "ret_value": {
                        "offset": 0,
                        "cairo_type": "(publicKey: felt)"
                    },
                    "range_check_ptr": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__wrappers__.getPublicKey_encode_return.ImplicitArgs": {
                "full_name": "__wrappers__.getPublicKey_encode_return.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.getPublicKey_encode_return.Return": {
                "cairo_type": "(range_check_ptr: felt, data_len: felt, data: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.getPublicKey_encode_return.SIZEOF_LOCALS": {
                "value": 1,
                "type": "const"
            },
            "__wrappers__.getPublicKey_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.isValidSignature": {
                "decorators": [
                    "view"
                ],
                "pc": 423,
                "type": "function"
            },
            "__wrappers__.isValidSignature.Args": {
                "full_name": "__wrappers__.isValidSignature.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.isValidSignature.ImplicitArgs": {
                "full_name": "__wrappers__.isValidSignature.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.isValidSignature.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: starkware.cairo.common.cairo_builtins.SignatureBuiltin*, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.isValidSignature.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.isValidSignature.__wrapped_func": {
                "destination": "__main__.isValidSignature",
                "type": "alias"
            },
            "__wrappers__.isValidSignature_encode_return": {
                "decorators": [],
                "pc": 414,
                "type": "function"
            },
            "__wrappers__.isValidSignature_encode_return.Args": {
                "full_name": "__wrappers__.isValidSignature_encode_return.Args",
                "size": 2,
                "members": {
                    "ret_value": {
                        "offset": 0,
                        "cairo_type": "(isValid: felt)"
                    },
                    "range_check_ptr": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__wrappers__.isValidSignature_encode_return.ImplicitArgs": {
                "full_name": "__wrappers__.isValidSignature_encode_return.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.isValidSignature_encode_return.Return": {
                "cairo_type": "(range_check_ptr: felt, data_len: felt, data: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.isValidSignature_encode_return.SIZEOF_LOCALS": {
                "value": 1,
                "type": "const"
            },
            "__wrappers__.isValidSignature_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.setPublicKey": {
                "decorators": [
                    "external"
                ],
                "pc": 384,
                "type": "function"
            },
            "__wrappers__.setPublicKey.Args": {
                "full_name": "__wrappers__.setPublicKey.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.setPublicKey.ImplicitArgs": {
                "full_name": "__wrappers__.setPublicKey.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.setPublicKey.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: felt, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.setPublicKey.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.setPublicKey.__wrapped_func": {
                "destination": "__main__.setPublicKey",
                "type": "alias"
            },
            "__wrappers__.setPublicKey_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "__wrappers__.supportsInterface": {
                "decorators": [
                    "view"
                ],
                "pc": 357,
                "type": "function"
            },
            "__wrappers__.supportsInterface.Args": {
                "full_name": "__wrappers__.supportsInterface.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.supportsInterface.ImplicitArgs": {
                "full_name": "__wrappers__.supportsInterface.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.supportsInterface.Return": {
                "cairo_type": "(syscall_ptr: felt*, pedersen_ptr: starkware.cairo.common.cairo_builtins.HashBuiltin*, range_check_ptr: felt, ecdsa_ptr: felt, bitwise_ptr: felt, size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.supportsInterface.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "__wrappers__.supportsInterface.__wrapped_func": {
                "destination": "__main__.supportsInterface",
                "type": "alias"
            },
            "__wrappers__.supportsInterface_encode_return": {
                "decorators": [],
                "pc": 348,
                "type": "function"
            },
            "__wrappers__.supportsInterface_encode_return.Args": {
                "full_name": "__wrappers__.supportsInterface_encode_return.Args",
                "size": 2,
                "members": {
                    "ret_value": {
                        "offset": 0,
                        "cairo_type": "(success: felt)"
                    },
                    "range_check_ptr": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "__wrappers__.supportsInterface_encode_return.ImplicitArgs": {
                "full_name": "__wrappers__.supportsInterface_encode_return.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "__wrappers__.supportsInterface_encode_return.Return": {
                "cairo_type": "(range_check_ptr: felt, data_len: felt, data: felt*)",
                "type": "type_definition"
            },
            "__wrappers__.supportsInterface_encode_return.SIZEOF_LOCALS": {
                "value": 1,
                "type": "const"
            },
            "__wrappers__.supportsInterface_encode_return.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "openzeppelin.account.library.Account": {
                "type": "namespace"
            },
            "openzeppelin.account.library.Account.Args": {
                "full_name": "openzeppelin.account.library.Account.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account._execute_list": {
                "decorators": [],
                "pc": 224,
                "type": "function"
            },
            "openzeppelin.account.library.Account._execute_list.Args": {
                "full_name": "openzeppelin.account.library.Account._execute_list.Args",
                "size": 3,
                "members": {
                    "calls_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "calls": {
                        "offset": 1,
                        "cairo_type": "openzeppelin.account.library.Call*"
                    },
                    "response": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account._execute_list.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account._execute_list.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account._execute_list.Return": {
                "cairo_type": "(response_len: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account._execute_list.SIZEOF_LOCALS": {
                "value": 3,
                "type": "const"
            },
            "openzeppelin.account.library.Account._from_call_array_to_call": {
                "decorators": [],
                "pc": 258,
                "type": "function"
            },
            "openzeppelin.account.library.Account._from_call_array_to_call.Args": {
                "full_name": "openzeppelin.account.library.Account._from_call_array_to_call.Args",
                "size": 4,
                "members": {
                    "call_array_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "call_array": {
                        "offset": 1,
                        "cairo_type": "openzeppelin.account.library.AccountCallArray*"
                    },
                    "calldata": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    },
                    "calls": {
                        "offset": 3,
                        "cairo_type": "openzeppelin.account.library.Call*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account._from_call_array_to_call.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account._from_call_array_to_call.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account._from_call_array_to_call.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account._from_call_array_to_call.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.assert_only_self": {
                "decorators": [],
                "pc": 109,
                "type": "function"
            },
            "openzeppelin.account.library.Account.assert_only_self.Args": {
                "full_name": "openzeppelin.account.library.Account.assert_only_self.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account.assert_only_self.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.assert_only_self.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.assert_only_self.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.assert_only_self.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.execute": {
                "decorators": [],
                "pc": 178,
                "type": "function"
            },
            "openzeppelin.account.library.Account.execute.Args": {
                "full_name": "openzeppelin.account.library.Account.execute.Args",
                "size": 4,
                "members": {
                    "call_array_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "call_array": {
                        "offset": 1,
                        "cairo_type": "openzeppelin.account.library.AccountCallArray*"
                    },
                    "calldata_len": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.execute.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.execute.ImplicitArgs",
                "size": 5,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "bitwise_ptr": {
                        "offset": 3,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 4,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.execute.Return": {
                "cairo_type": "(response_len: felt, response: felt*)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.execute.SIZEOF_LOCALS": {
                "value": 2,
                "type": "const"
            },
            "openzeppelin.account.library.Account.get_public_key": {
                "decorators": [],
                "pc": 118,
                "type": "function"
            },
            "openzeppelin.account.library.Account.get_public_key.Args": {
                "full_name": "openzeppelin.account.library.Account.get_public_key.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account.get_public_key.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.get_public_key.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.get_public_key.Return": {
                "cairo_type": "(public_key: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.get_public_key.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.initializer": {
                "decorators": [],
                "pc": 102,
                "type": "function"
            },
            "openzeppelin.account.library.Account.initializer.Args": {
                "full_name": "openzeppelin.account.library.Account.initializer.Args",
                "size": 1,
                "members": {
                    "_public_key": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.initializer.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.initializer.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.initializer.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.initializer.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.is_valid_signature": {
                "decorators": [],
                "pc": 159,
                "type": "function"
            },
            "openzeppelin.account.library.Account.is_valid_signature.Args": {
                "full_name": "openzeppelin.account.library.Account.is_valid_signature.Args",
                "size": 3,
                "members": {
                    "hash": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "signature_len": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "signature": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.is_valid_signature.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.is_valid_signature.ImplicitArgs",
                "size": 4,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "ecdsa_ptr": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.is_valid_signature.Return": {
                "cairo_type": "(is_valid: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.is_valid_signature.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.set_public_key": {
                "decorators": [],
                "pc": 150,
                "type": "function"
            },
            "openzeppelin.account.library.Account.set_public_key.Args": {
                "full_name": "openzeppelin.account.library.Account.set_public_key.Args",
                "size": 1,
                "members": {
                    "new_public_key": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.set_public_key.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.set_public_key.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.set_public_key.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.set_public_key.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account.supports_interface": {
                "decorators": [],
                "pc": 124,
                "type": "function"
            },
            "openzeppelin.account.library.Account.supports_interface.Args": {
                "full_name": "openzeppelin.account.library.Account.supports_interface.Args",
                "size": 1,
                "members": {
                    "interface_id": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.supports_interface.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account.supports_interface.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account.supports_interface.Return": {
                "cairo_type": "(success: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account.supports_interface.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.AccountCallArray": {
                "full_name": "openzeppelin.account.library.AccountCallArray",
                "size": 4,
                "members": {
                    "to": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "selector": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "data_offset": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "data_len": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key": {
                "type": "namespace"
            },
            "openzeppelin.account.library.Account_public_key.Args": {
                "full_name": "openzeppelin.account.library.Account_public_key.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.HashBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "type": "alias"
            },
            "openzeppelin.account.library.Account_public_key.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account_public_key.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account_public_key.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account_public_key.addr": {
                "decorators": [],
                "pc": 72,
                "type": "function"
            },
            "openzeppelin.account.library.Account_public_key.addr.Args": {
                "full_name": "openzeppelin.account.library.Account_public_key.addr.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.addr.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account_public_key.addr.ImplicitArgs",
                "size": 2,
                "members": {
                    "pedersen_ptr": {
                        "offset": 0,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.addr.Return": {
                "cairo_type": "(res: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account_public_key.addr.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account_public_key.hash2": {
                "destination": "starkware.cairo.common.hash.hash2",
                "type": "alias"
            },
            "openzeppelin.account.library.Account_public_key.normalize_address": {
                "destination": "starkware.starknet.common.storage.normalize_address",
                "type": "alias"
            },
            "openzeppelin.account.library.Account_public_key.read": {
                "decorators": [],
                "pc": 77,
                "type": "function"
            },
            "openzeppelin.account.library.Account_public_key.read.Args": {
                "full_name": "openzeppelin.account.library.Account_public_key.read.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.read.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account_public_key.read.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.read.Return": {
                "cairo_type": "(public_key: felt)",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account_public_key.read.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.Account_public_key.storage_read": {
                "destination": "starkware.starknet.common.syscalls.storage_read",
                "type": "alias"
            },
            "openzeppelin.account.library.Account_public_key.storage_write": {
                "destination": "starkware.starknet.common.syscalls.storage_write",
                "type": "alias"
            },
            "openzeppelin.account.library.Account_public_key.write": {
                "decorators": [],
                "pc": 90,
                "type": "function"
            },
            "openzeppelin.account.library.Account_public_key.write.Args": {
                "full_name": "openzeppelin.account.library.Account_public_key.write.Args",
                "size": 1,
                "members": {
                    "value": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.write.ImplicitArgs": {
                "full_name": "openzeppelin.account.library.Account_public_key.write.ImplicitArgs",
                "size": 3,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "pedersen_ptr": {
                        "offset": 1,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.HashBuiltin*"
                    },
                    "range_check_ptr": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.Account_public_key.write.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "openzeppelin.account.library.Account_public_key.write.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.account.library.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "openzeppelin.account.library.Call": {
                "full_name": "openzeppelin.account.library.Call",
                "size": 4,
                "members": {
                    "to": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "selector": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "calldata_len": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "openzeppelin.account.library.FALSE": {
                "destination": "starkware.cairo.common.bool.FALSE",
                "type": "alias"
            },
            "openzeppelin.account.library.HashBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "type": "alias"
            },
            "openzeppelin.account.library.IACCOUNT_ID": {
                "destination": "openzeppelin.utils.constants.library.IACCOUNT_ID",
                "type": "alias"
            },
            "openzeppelin.account.library.IERC165_ID": {
                "destination": "openzeppelin.utils.constants.library.IERC165_ID",
                "type": "alias"
            },
            "openzeppelin.account.library.SignatureBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.SignatureBuiltin",
                "type": "alias"
            },
            "openzeppelin.account.library.TRUE": {
                "destination": "starkware.cairo.common.bool.TRUE",
                "type": "alias"
            },
            "openzeppelin.account.library.Uint256": {
                "destination": "starkware.cairo.common.uint256.Uint256",
                "type": "alias"
            },
            "openzeppelin.account.library.alloc": {
                "destination": "starkware.cairo.common.alloc.alloc",
                "type": "alias"
            },
            "openzeppelin.account.library.call_contract": {
                "destination": "starkware.starknet.common.syscalls.call_contract",
                "type": "alias"
            },
            "openzeppelin.account.library.get_caller_address": {
                "destination": "starkware.starknet.common.syscalls.get_caller_address",
                "type": "alias"
            },
            "openzeppelin.account.library.get_contract_address": {
                "destination": "starkware.starknet.common.syscalls.get_contract_address",
                "type": "alias"
            },
            "openzeppelin.account.library.get_fp_and_pc": {
                "destination": "starkware.cairo.common.registers.get_fp_and_pc",
                "type": "alias"
            },
            "openzeppelin.account.library.get_tx_info": {
                "destination": "starkware.starknet.common.syscalls.get_tx_info",
                "type": "alias"
            },
            "openzeppelin.account.library.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "openzeppelin.account.library.split_felt": {
                "destination": "starkware.cairo.common.math.split_felt",
                "type": "alias"
            },
            "openzeppelin.account.library.verify_ecdsa_signature": {
                "destination": "starkware.cairo.common.signature.verify_ecdsa_signature",
                "type": "alias"
            },
            "openzeppelin.account.library.verify_eth_signature_uint256": {
                "destination": "starkware.cairo.common.cairo_secp.signature.verify_eth_signature_uint256",
                "type": "alias"
            },
            "openzeppelin.utils.constants.library.DEFAULT_ADMIN_ROLE": {
                "value": 0,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IACCESSCONTROL_ID": {
                "value": 2036718347,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IACCOUNT_ID": {
                "value": 2792084853,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IERC165_ID": {
                "value": 33540519,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IERC721_ENUMERABLE_ID": {
                "value": 2014223715,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IERC721_ID": {
                "value": 2158778573,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IERC721_METADATA_ID": {
                "value": 1532892063,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.IERC721_RECEIVER_ID": {
                "value": 353073666,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.INVALID_ID": {
                "value": 4294967295,
                "type": "const"
            },
            "openzeppelin.utils.constants.library.UINT8_MAX": {
                "value": 255,
                "type": "const"
            },
            "starkware.cairo.common.alloc.alloc": {
                "decorators": [],
                "pc": 0,
                "type": "function"
            },
            "starkware.cairo.common.alloc.alloc.Args": {
                "full_name": "starkware.cairo.common.alloc.alloc.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.cairo.common.alloc.alloc.ImplicitArgs": {
                "full_name": "starkware.cairo.common.alloc.alloc.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.cairo.common.alloc.alloc.Return": {
                "cairo_type": "(ptr: felt*)",
                "type": "type_definition"
            },
            "starkware.cairo.common.alloc.alloc.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.cairo.common.bitwise.ALL_ONES": {
                "value": -106710729501573572985208420194530329073740042555888586719234,
                "type": "const"
            },
            "starkware.cairo.common.bitwise.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.bool.FALSE": {
                "value": 0,
                "type": "const"
            },
            "starkware.cairo.common.bool.TRUE": {
                "value": 1,
                "type": "const"
            },
            "starkware.cairo.common.cairo_builtins.BitwiseBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "size": 5,
                "members": {
                    "x": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "y": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "x_and_y": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "x_xor_y": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "x_or_y": {
                        "offset": 4,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.EcOpBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.EcOpBuiltin",
                "size": 7,
                "members": {
                    "p": {
                        "offset": 0,
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint"
                    },
                    "q": {
                        "offset": 2,
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint"
                    },
                    "m": {
                        "offset": 4,
                        "cairo_type": "felt"
                    },
                    "r": {
                        "offset": 5,
                        "cairo_type": "starkware.cairo.common.ec_point.EcPoint"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.EcPoint": {
                "destination": "starkware.cairo.common.ec_point.EcPoint",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_builtins.HashBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "size": 3,
                "members": {
                    "x": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "y": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "result": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.KeccakBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.KeccakBuiltin",
                "size": 16,
                "members": {
                    "input": {
                        "offset": 0,
                        "cairo_type": "starkware.cairo.common.keccak_state.KeccakBuiltinState"
                    },
                    "output": {
                        "offset": 8,
                        "cairo_type": "starkware.cairo.common.keccak_state.KeccakBuiltinState"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_builtins.KeccakBuiltinState": {
                "destination": "starkware.cairo.common.keccak_state.KeccakBuiltinState",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_builtins.SignatureBuiltin": {
                "full_name": "starkware.cairo.common.cairo_builtins.SignatureBuiltin",
                "size": 2,
                "members": {
                    "pub_key": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "message": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_keccak.keccak.BLOCK_SIZE": {
                "destination": "starkware.cairo.common.cairo_keccak.packed_keccak.BLOCK_SIZE",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.BYTES_IN_WORD": {
                "value": 8,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.keccak.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.KECCAK_CAPACITY_IN_WORDS": {
                "value": 8,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.keccak.KECCAK_FULL_RATE_IN_BYTES": {
                "value": 136,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.keccak.KECCAK_FULL_RATE_IN_WORDS": {
                "value": 17,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.keccak.KECCAK_STATE_SIZE_FELTS": {
                "value": 25,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.keccak.Uint256": {
                "destination": "starkware.cairo.common.uint256.Uint256",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.alloc": {
                "destination": "starkware.cairo.common.alloc.alloc",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.assert_lt": {
                "destination": "starkware.cairo.common.math.assert_lt",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.assert_nn": {
                "destination": "starkware.cairo.common.math.assert_nn",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.assert_nn_le": {
                "destination": "starkware.cairo.common.math.assert_nn_le",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.assert_not_zero": {
                "destination": "starkware.cairo.common.math.assert_not_zero",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.bitwise_and": {
                "destination": "starkware.cairo.common.bitwise.bitwise_and",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.bitwise_or": {
                "destination": "starkware.cairo.common.bitwise.bitwise_or",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.bitwise_xor": {
                "destination": "starkware.cairo.common.bitwise.bitwise_xor",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.memcpy": {
                "destination": "starkware.cairo.common.memcpy.memcpy",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.memset": {
                "destination": "starkware.cairo.common.memset.memset",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.packed_keccak_func": {
                "destination": "starkware.cairo.common.cairo_keccak.packed_keccak.packed_keccak_func",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.pow": {
                "destination": "starkware.cairo.common.pow.pow",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.split_felt": {
                "destination": "starkware.cairo.common.math.split_felt",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.uint256_reverse_endian": {
                "destination": "starkware.cairo.common.uint256.uint256_reverse_endian",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.keccak.unsigned_div_rem": {
                "destination": "starkware.cairo.common.math.unsigned_div_rem",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.ALL_ONES": {
                "value": -106710729501573572985208420194530329073740042555888586719234,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.BLOCK_SIZE": {
                "value": 3,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.SHIFTS": {
                "value": 340282366920938463481821351505477763073,
                "type": "const"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.alloc": {
                "destination": "starkware.cairo.common.alloc.alloc",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_keccak.packed_keccak.get_fp_and_pc": {
                "destination": "starkware.cairo.common.registers.get_fp_and_pc",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.BASE": {
                "destination": "starkware.cairo.common.cairo_secp.constants.BASE",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.BigInt3": {
                "full_name": "starkware.cairo.common.cairo_secp.bigint.BigInt3",
                "size": 3,
                "members": {
                    "d0": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "d1": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "d2": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_secp.bigint.RC_BOUND": {
                "destination": "starkware.cairo.common.math_cmp.RC_BOUND",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.Uint256": {
                "destination": "starkware.cairo.common.uint256.Uint256",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt3": {
                "full_name": "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt3",
                "size": 3,
                "members": {
                    "d0": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "d1": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "d2": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt5": {
                "full_name": "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt5",
                "size": 5,
                "members": {
                    "d0": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "d1": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "d2": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "d3": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "d4": {
                        "offset": 4,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_secp.bigint.assert_nn": {
                "destination": "starkware.cairo.common.math.assert_nn",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.assert_nn_le": {
                "destination": "starkware.cairo.common.math.assert_nn_le",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.bigint.unsigned_div_rem": {
                "destination": "starkware.cairo.common.math.unsigned_div_rem",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.constants.BASE": {
                "value": 77371252455336267181195264,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.BETA": {
                "value": 7,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.N0": {
                "value": 10428087374290690730508609,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.N1": {
                "value": 77371252455330678278691517,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.N2": {
                "value": 19342813113834066795298815,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.P0": {
                "value": 77371252455336262886226991,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.P1": {
                "value": 77371252455336267181195263,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.P2": {
                "value": 19342813113834066795298815,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.constants.SECP_REM": {
                "value": 4294968273,
                "type": "const"
            },
            "starkware.cairo.common.cairo_secp.ec.BigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.BigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.EcPoint": {
                "full_name": "starkware.cairo.common.cairo_secp.ec.EcPoint",
                "size": 6,
                "members": {
                    "x": {
                        "offset": 0,
                        "cairo_type": "starkware.cairo.common.cairo_secp.bigint.BigInt3"
                    },
                    "y": {
                        "offset": 3,
                        "cairo_type": "starkware.cairo.common.cairo_secp.bigint.BigInt3"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.cairo_secp.ec.UnreducedBigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.is_zero": {
                "destination": "starkware.cairo.common.cairo_secp.field.is_zero",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.nondet_bigint3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.nondet_bigint3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.unreduced_mul": {
                "destination": "starkware.cairo.common.cairo_secp.field.unreduced_mul",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.unreduced_sqr": {
                "destination": "starkware.cairo.common.cairo_secp.field.unreduced_sqr",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.ec.verify_zero": {
                "destination": "starkware.cairo.common.cairo_secp.field.verify_zero",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.BASE": {
                "destination": "starkware.cairo.common.cairo_secp.constants.BASE",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.BigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.BigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.P0": {
                "destination": "starkware.cairo.common.cairo_secp.constants.P0",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.P1": {
                "destination": "starkware.cairo.common.cairo_secp.constants.P1",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.P2": {
                "destination": "starkware.cairo.common.cairo_secp.constants.P2",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.SECP_REM": {
                "destination": "starkware.cairo.common.cairo_secp.constants.SECP_REM",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.UnreducedBigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.assert_nn_le": {
                "destination": "starkware.cairo.common.math.assert_nn_le",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.field.nondet_bigint3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.nondet_bigint3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.BASE": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.BASE",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.BETA": {
                "destination": "starkware.cairo.common.cairo_secp.constants.BETA",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.BigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.BigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.EcPoint": {
                "destination": "starkware.cairo.common.cairo_secp.ec.EcPoint",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.N0": {
                "destination": "starkware.cairo.common.cairo_secp.constants.N0",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.N1": {
                "destination": "starkware.cairo.common.cairo_secp.constants.N1",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.N2": {
                "destination": "starkware.cairo.common.cairo_secp.constants.N2",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.RC_BOUND": {
                "destination": "starkware.cairo.common.math_cmp.RC_BOUND",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.Uint256": {
                "destination": "starkware.cairo.common.uint256.Uint256",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.UnreducedBigInt3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.UnreducedBigInt3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.alloc": {
                "destination": "starkware.cairo.common.alloc.alloc",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.assert_nn": {
                "destination": "starkware.cairo.common.math.assert_nn",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.assert_nn_le": {
                "destination": "starkware.cairo.common.math.assert_nn_le",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.assert_not_zero": {
                "destination": "starkware.cairo.common.math.assert_not_zero",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.bigint_mul": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.bigint_mul",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.bigint_to_uint256": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.bigint_to_uint256",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.ec_add": {
                "destination": "starkware.cairo.common.cairo_secp.ec.ec_add",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.ec_mul": {
                "destination": "starkware.cairo.common.cairo_secp.ec.ec_mul",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.ec_negate": {
                "destination": "starkware.cairo.common.cairo_secp.ec.ec_negate",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.finalize_keccak": {
                "destination": "starkware.cairo.common.cairo_keccak.keccak.finalize_keccak",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.keccak_uint256s_bigend": {
                "destination": "starkware.cairo.common.cairo_keccak.keccak.keccak_uint256s_bigend",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.nondet_bigint3": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.nondet_bigint3",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.reduce": {
                "destination": "starkware.cairo.common.cairo_secp.field.reduce",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.uint256_to_bigint": {
                "destination": "starkware.cairo.common.cairo_secp.bigint.uint256_to_bigint",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.unreduced_mul": {
                "destination": "starkware.cairo.common.cairo_secp.field.unreduced_mul",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.unreduced_sqr": {
                "destination": "starkware.cairo.common.cairo_secp.field.unreduced_sqr",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.unsigned_div_rem": {
                "destination": "starkware.cairo.common.math.unsigned_div_rem",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.validate_reduced_field_element": {
                "destination": "starkware.cairo.common.cairo_secp.field.validate_reduced_field_element",
                "type": "alias"
            },
            "starkware.cairo.common.cairo_secp.signature.verify_zero": {
                "destination": "starkware.cairo.common.cairo_secp.field.verify_zero",
                "type": "alias"
            },
            "starkware.cairo.common.dict_access.DictAccess": {
                "full_name": "starkware.cairo.common.dict_access.DictAccess",
                "size": 3,
                "members": {
                    "key": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "prev_value": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "new_value": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.ec.EcOpBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.EcOpBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.ec.EcPoint": {
                "destination": "starkware.cairo.common.ec_point.EcPoint",
                "type": "alias"
            },
            "starkware.cairo.common.ec.StarkCurve": {
                "type": "namespace"
            },
            "starkware.cairo.common.ec.StarkCurve.ALPHA": {
                "value": 1,
                "type": "const"
            },
            "starkware.cairo.common.ec.StarkCurve.Args": {
                "full_name": "starkware.cairo.common.ec.StarkCurve.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.cairo.common.ec.StarkCurve.BETA": {
                "value": -476910135076337975234679399815567221425937815956490878998147463828055613816,
                "type": "const"
            },
            "starkware.cairo.common.ec.StarkCurve.GEN_X": {
                "value": 874739451078007766457464989774322083649278607533249481151382481072868806602,
                "type": "const"
            },
            "starkware.cairo.common.ec.StarkCurve.GEN_Y": {
                "value": 152666792071518830868575557812948353041420400780739481342941381225525861407,
                "type": "const"
            },
            "starkware.cairo.common.ec.StarkCurve.ImplicitArgs": {
                "full_name": "starkware.cairo.common.ec.StarkCurve.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.cairo.common.ec.StarkCurve.ORDER": {
                "value": -96363463615509210819012598251359154898,
                "type": "const"
            },
            "starkware.cairo.common.ec.StarkCurve.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "starkware.cairo.common.ec.StarkCurve.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.cairo.common.ec.is_quad_residue": {
                "destination": "starkware.cairo.common.math.is_quad_residue",
                "type": "alias"
            },
            "starkware.cairo.common.ec_point.EcPoint": {
                "full_name": "starkware.cairo.common.ec_point.EcPoint",
                "size": 2,
                "members": {
                    "x": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "y": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.hash.HashBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.HashBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.keccak_state.KeccakBuiltinState": {
                "full_name": "starkware.cairo.common.keccak_state.KeccakBuiltinState",
                "size": 8,
                "members": {
                    "s0": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "s1": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "s2": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "s3": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "s4": {
                        "offset": 4,
                        "cairo_type": "felt"
                    },
                    "s5": {
                        "offset": 5,
                        "cairo_type": "felt"
                    },
                    "s6": {
                        "offset": 6,
                        "cairo_type": "felt"
                    },
                    "s7": {
                        "offset": 7,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.math.FALSE": {
                "destination": "starkware.cairo.common.bool.FALSE",
                "type": "alias"
            },
            "starkware.cairo.common.math.TRUE": {
                "destination": "starkware.cairo.common.bool.TRUE",
                "type": "alias"
            },
            "starkware.cairo.common.math_cmp.RC_BOUND": {
                "value": 340282366920938463463374607431768211456,
                "type": "const"
            },
            "starkware.cairo.common.math_cmp.assert_le_felt": {
                "destination": "starkware.cairo.common.math.assert_le_felt",
                "type": "alias"
            },
            "starkware.cairo.common.math_cmp.assert_lt_felt": {
                "destination": "starkware.cairo.common.math.assert_lt_felt",
                "type": "alias"
            },
            "starkware.cairo.common.memcpy.memcpy": {
                "decorators": [],
                "pc": 3,
                "type": "function"
            },
            "starkware.cairo.common.memcpy.memcpy.Args": {
                "full_name": "starkware.cairo.common.memcpy.memcpy.Args",
                "size": 3,
                "members": {
                    "dst": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "src": {
                        "offset": 1,
                        "cairo_type": "felt*"
                    },
                    "len": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.memcpy.memcpy.ImplicitArgs": {
                "full_name": "starkware.cairo.common.memcpy.memcpy.ImplicitArgs",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.cairo.common.memcpy.memcpy.LoopFrame": {
                "full_name": "starkware.cairo.common.memcpy.memcpy.LoopFrame",
                "size": 2,
                "members": {
                    "dst": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    },
                    "src": {
                        "offset": 1,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.memcpy.memcpy.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "starkware.cairo.common.memcpy.memcpy.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.cairo.common.memcpy.memcpy.continue_copying": {
                "cairo_type": "felt",
                "full_name": "starkware.cairo.common.memcpy.memcpy.continue_copying",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 3,
                            "group": 1
                        },
                        "pc": 10,
                        "value": "[cast(ap, felt*)]"
                    }
                ],
                "type": "reference"
            },
            "starkware.cairo.common.memcpy.memcpy.len": {
                "cairo_type": "felt",
                "full_name": "starkware.cairo.common.memcpy.memcpy.len",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 1
                        },
                        "pc": 3,
                        "value": "[cast(fp + (-3), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "starkware.cairo.common.memcpy.memcpy.loop": {
                "pc": 8,
                "type": "label"
            },
            "starkware.cairo.common.pow.assert_le": {
                "destination": "starkware.cairo.common.math.assert_le",
                "type": "alias"
            },
            "starkware.cairo.common.pow.get_ap": {
                "destination": "starkware.cairo.common.registers.get_ap",
                "type": "alias"
            },
            "starkware.cairo.common.pow.get_fp_and_pc": {
                "destination": "starkware.cairo.common.registers.get_fp_and_pc",
                "type": "alias"
            },
            "starkware.cairo.common.registers.get_ap": {
                "destination": "starkware.cairo.lang.compiler.lib.registers.get_ap",
                "type": "alias"
            },
            "starkware.cairo.common.registers.get_fp_and_pc": {
                "destination": "starkware.cairo.lang.compiler.lib.registers.get_fp_and_pc",
                "type": "alias"
            },
            "starkware.cairo.common.signature.EcOpBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.EcOpBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.signature.EcPoint": {
                "destination": "starkware.cairo.common.ec_point.EcPoint",
                "type": "alias"
            },
            "starkware.cairo.common.signature.FALSE": {
                "destination": "starkware.cairo.common.bool.FALSE",
                "type": "alias"
            },
            "starkware.cairo.common.signature.SignatureBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.SignatureBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.signature.StarkCurve": {
                "destination": "starkware.cairo.common.ec.StarkCurve",
                "type": "alias"
            },
            "starkware.cairo.common.signature.TRUE": {
                "destination": "starkware.cairo.common.bool.TRUE",
                "type": "alias"
            },
            "starkware.cairo.common.signature.ec_add": {
                "destination": "starkware.cairo.common.ec.ec_add",
                "type": "alias"
            },
            "starkware.cairo.common.signature.ec_mul": {
                "destination": "starkware.cairo.common.ec.ec_mul",
                "type": "alias"
            },
            "starkware.cairo.common.signature.ec_sub": {
                "destination": "starkware.cairo.common.ec.ec_sub",
                "type": "alias"
            },
            "starkware.cairo.common.signature.is_x_on_curve": {
                "destination": "starkware.cairo.common.ec.is_x_on_curve",
                "type": "alias"
            },
            "starkware.cairo.common.signature.recover_y": {
                "destination": "starkware.cairo.common.ec.recover_y",
                "type": "alias"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature": {
                "decorators": [],
                "pc": 67,
                "type": "function"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.Args": {
                "full_name": "starkware.cairo.common.signature.verify_ecdsa_signature.Args",
                "size": 4,
                "members": {
                    "message": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "public_key": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "signature_r": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "signature_s": {
                        "offset": 3,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.ImplicitArgs": {
                "full_name": "starkware.cairo.common.signature.verify_ecdsa_signature.ImplicitArgs",
                "size": 1,
                "members": {
                    "ecdsa_ptr": {
                        "offset": 0,
                        "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.ecdsa_ptr": {
                "cairo_type": "starkware.cairo.common.cairo_builtins.SignatureBuiltin*",
                "full_name": "starkware.cairo.common.signature.verify_ecdsa_signature.ecdsa_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 8
                        },
                        "pc": 67,
                        "value": "[cast(fp + (-7), starkware.cairo.common.cairo_builtins.SignatureBuiltin**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 8
                        },
                        "pc": 69,
                        "value": "cast([fp + (-7)] + 2, starkware.cairo.common.cairo_builtins.SignatureBuiltin*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.signature_r": {
                "cairo_type": "felt",
                "full_name": "starkware.cairo.common.signature.verify_ecdsa_signature.signature_r",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 8
                        },
                        "pc": 67,
                        "value": "[cast(fp + (-4), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "starkware.cairo.common.signature.verify_ecdsa_signature.signature_s": {
                "cairo_type": "felt",
                "full_name": "starkware.cairo.common.signature.verify_ecdsa_signature.signature_s",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 8
                        },
                        "pc": 67,
                        "value": "[cast(fp + (-3), felt*)]"
                    }
                ],
                "type": "reference"
            },
            "starkware.cairo.common.uint256.ALL_ONES": {
                "value": 340282366920938463463374607431768211455,
                "type": "const"
            },
            "starkware.cairo.common.uint256.BitwiseBuiltin": {
                "destination": "starkware.cairo.common.cairo_builtins.BitwiseBuiltin",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.HALF_SHIFT": {
                "value": 18446744073709551616,
                "type": "const"
            },
            "starkware.cairo.common.uint256.SHIFT": {
                "value": 340282366920938463463374607431768211456,
                "type": "const"
            },
            "starkware.cairo.common.uint256.Uint256": {
                "full_name": "starkware.cairo.common.uint256.Uint256",
                "size": 2,
                "members": {
                    "low": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "high": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.cairo.common.uint256.assert_in_range": {
                "destination": "starkware.cairo.common.math.assert_in_range",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.assert_le": {
                "destination": "starkware.cairo.common.math.assert_le",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.assert_nn_le": {
                "destination": "starkware.cairo.common.math.assert_nn_le",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.assert_not_zero": {
                "destination": "starkware.cairo.common.math.assert_not_zero",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.bitwise_and": {
                "destination": "starkware.cairo.common.bitwise.bitwise_and",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.bitwise_or": {
                "destination": "starkware.cairo.common.bitwise.bitwise_or",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.bitwise_xor": {
                "destination": "starkware.cairo.common.bitwise.bitwise_xor",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.get_ap": {
                "destination": "starkware.cairo.common.registers.get_ap",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.get_fp_and_pc": {
                "destination": "starkware.cairo.common.registers.get_fp_and_pc",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.is_le": {
                "destination": "starkware.cairo.common.math_cmp.is_le",
                "type": "alias"
            },
            "starkware.cairo.common.uint256.pow": {
                "destination": "starkware.cairo.common.pow.pow",
                "type": "alias"
            },
            "starkware.starknet.common.storage.ADDR_BOUND": {
                "value": -106710729501573572985208420194530329073740042555888586719489,
                "type": "const"
            },
            "starkware.starknet.common.storage.MAX_STORAGE_ITEM_SIZE": {
                "value": 256,
                "type": "const"
            },
            "starkware.starknet.common.storage.assert_250_bit": {
                "destination": "starkware.cairo.common.math.assert_250_bit",
                "type": "alias"
            },
            "starkware.starknet.common.syscalls.CALL_CONTRACT_SELECTOR": {
                "value": 20853273475220472486191784820,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.CallContract": {
                "full_name": "starkware.starknet.common.syscalls.CallContract",
                "size": 7,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.CallContractRequest"
                    },
                    "response": {
                        "offset": 5,
                        "cairo_type": "starkware.starknet.common.syscalls.CallContractResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.CallContractRequest": {
                "full_name": "starkware.starknet.common.syscalls.CallContractRequest",
                "size": 5,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "contract_address": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "function_selector": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata_size": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 4,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.CallContractResponse": {
                "full_name": "starkware.starknet.common.syscalls.CallContractResponse",
                "size": 2,
                "members": {
                    "retdata_size": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "retdata": {
                        "offset": 1,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.DELEGATE_CALL_SELECTOR": {
                "value": 21167594061783206823196716140,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.DELEGATE_L1_HANDLER_SELECTOR": {
                "value": 23274015802972845247556842986379118667122,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.DEPLOY_SELECTOR": {
                "value": 75202468540281,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.Deploy": {
                "full_name": "starkware.starknet.common.syscalls.Deploy",
                "size": 9,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.DeployRequest"
                    },
                    "response": {
                        "offset": 6,
                        "cairo_type": "starkware.starknet.common.syscalls.DeployResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.DeployRequest": {
                "full_name": "starkware.starknet.common.syscalls.DeployRequest",
                "size": 6,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "class_hash": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "contract_address_salt": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "constructor_calldata_size": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "constructor_calldata": {
                        "offset": 4,
                        "cairo_type": "felt*"
                    },
                    "deploy_from_zero": {
                        "offset": 5,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.DeployResponse": {
                "full_name": "starkware.starknet.common.syscalls.DeployResponse",
                "size": 3,
                "members": {
                    "contract_address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "constructor_retdata_size": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "constructor_retdata": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.DictAccess": {
                "destination": "starkware.cairo.common.dict_access.DictAccess",
                "type": "alias"
            },
            "starkware.starknet.common.syscalls.EMIT_EVENT_SELECTOR": {
                "value": 1280709301550335749748,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.EmitEvent": {
                "full_name": "starkware.starknet.common.syscalls.EmitEvent",
                "size": 5,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "keys_len": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "keys": {
                        "offset": 2,
                        "cairo_type": "felt*"
                    },
                    "data_len": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "data": {
                        "offset": 4,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GET_BLOCK_NUMBER_SELECTOR": {
                "value": 1448089106835523001438702345020786,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_BLOCK_TIMESTAMP_SELECTOR": {
                "value": 24294903732626645868215235778792757751152,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_CALLER_ADDRESS_SELECTOR": {
                "value": 94901967781393078444254803017658102643,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_CONTRACT_ADDRESS_SELECTOR": {
                "value": 6219495360805491471215297013070624192820083,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_SEQUENCER_ADDRESS_SELECTOR": {
                "value": 1592190833581991703053805829594610833820054387,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_TX_INFO_SELECTOR": {
                "value": 1317029390204112103023,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GET_TX_SIGNATURE_SELECTOR": {
                "value": 1448089128652340074717162277007973,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.GetBlockNumber": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumber",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockNumberRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockNumberResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockNumberRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumberRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockNumberResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockNumberResponse",
                "size": 1,
                "members": {
                    "block_number": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestamp": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestamp",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockTimestampRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetBlockTimestampResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestampRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestampRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetBlockTimestampResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetBlockTimestampResponse",
                "size": 1,
                "members": {
                    "block_timestamp": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddress",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetCallerAddressRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetCallerAddressResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddressRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetCallerAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetCallerAddressResponse",
                "size": 1,
                "members": {
                    "caller_address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddress",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetContractAddressRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetContractAddressResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddressRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetContractAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetContractAddressResponse",
                "size": 1,
                "members": {
                    "contract_address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddress": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddress",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetSequencerAddressRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetSequencerAddressResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddressRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddressRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetSequencerAddressResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetSequencerAddressResponse",
                "size": 1,
                "members": {
                    "sequencer_address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfo": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfo",
                "size": 2,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxInfoRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxInfoResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfoRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfoRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxInfoResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetTxInfoResponse",
                "size": 1,
                "members": {
                    "tx_info": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.TxInfo*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignature": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignature",
                "size": 3,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxSignatureRequest"
                    },
                    "response": {
                        "offset": 1,
                        "cairo_type": "starkware.starknet.common.syscalls.GetTxSignatureResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignatureRequest": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignatureRequest",
                "size": 1,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.GetTxSignatureResponse": {
                "full_name": "starkware.starknet.common.syscalls.GetTxSignatureResponse",
                "size": 2,
                "members": {
                    "signature_len": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "signature": {
                        "offset": 1,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.LIBRARY_CALL_L1_HANDLER_SELECTOR": {
                "value": 436233452754198157705746250789557519228244616562,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.LIBRARY_CALL_SELECTOR": {
                "value": 92376026794327011772951660,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.LibraryCall": {
                "full_name": "starkware.starknet.common.syscalls.LibraryCall",
                "size": 7,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.LibraryCallRequest"
                    },
                    "response": {
                        "offset": 5,
                        "cairo_type": "starkware.starknet.common.syscalls.CallContractResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.LibraryCallRequest": {
                "full_name": "starkware.starknet.common.syscalls.LibraryCallRequest",
                "size": 5,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "class_hash": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "function_selector": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata_size": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 4,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.SEND_MESSAGE_TO_L1_SELECTOR": {
                "value": 433017908768303439907196859243777073,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.STORAGE_READ_SELECTOR": {
                "value": 100890693370601760042082660,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.STORAGE_WRITE_SELECTOR": {
                "value": 25828017502874050592466629733,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.SendMessageToL1SysCall": {
                "full_name": "starkware.starknet.common.syscalls.SendMessageToL1SysCall",
                "size": 4,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "to_address": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "payload_size": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "payload_ptr": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageRead": {
                "full_name": "starkware.starknet.common.syscalls.StorageRead",
                "size": 3,
                "members": {
                    "request": {
                        "offset": 0,
                        "cairo_type": "starkware.starknet.common.syscalls.StorageReadRequest"
                    },
                    "response": {
                        "offset": 2,
                        "cairo_type": "starkware.starknet.common.syscalls.StorageReadResponse"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageReadRequest": {
                "full_name": "starkware.starknet.common.syscalls.StorageReadRequest",
                "size": 2,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "address": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageReadResponse": {
                "full_name": "starkware.starknet.common.syscalls.StorageReadResponse",
                "size": 1,
                "members": {
                    "value": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.StorageWrite": {
                "full_name": "starkware.starknet.common.syscalls.StorageWrite",
                "size": 3,
                "members": {
                    "selector": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "address": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "value": {
                        "offset": 2,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.TxInfo": {
                "full_name": "starkware.starknet.common.syscalls.TxInfo",
                "size": 8,
                "members": {
                    "version": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "account_contract_address": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "max_fee": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "signature_len": {
                        "offset": 3,
                        "cairo_type": "felt"
                    },
                    "signature": {
                        "offset": 4,
                        "cairo_type": "felt*"
                    },
                    "transaction_hash": {
                        "offset": 5,
                        "cairo_type": "felt"
                    },
                    "chain_id": {
                        "offset": 6,
                        "cairo_type": "felt"
                    },
                    "nonce": {
                        "offset": 7,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.call_contract": {
                "decorators": [],
                "pc": 18,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.call_contract.Args": {
                "full_name": "starkware.starknet.common.syscalls.call_contract.Args",
                "size": 4,
                "members": {
                    "contract_address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "function_selector": {
                        "offset": 1,
                        "cairo_type": "felt"
                    },
                    "calldata_size": {
                        "offset": 2,
                        "cairo_type": "felt"
                    },
                    "calldata": {
                        "offset": 3,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.call_contract.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.call_contract.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.call_contract.Return": {
                "cairo_type": "(retdata_size: felt, retdata: felt*)",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.call_contract.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.call_contract.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.call_contract.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 2
                        },
                        "pc": 18,
                        "value": "[cast(fp + (-7), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 2
                        },
                        "pc": 25,
                        "value": "cast([fp + (-7)] + 7, felt*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.starknet.common.syscalls.get_caller_address": {
                "decorators": [],
                "pc": 30,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.get_caller_address.Args": {
                "full_name": "starkware.starknet.common.syscalls.get_caller_address.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_caller_address.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.get_caller_address.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_caller_address.Return": {
                "cairo_type": "(caller_address: felt)",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.get_caller_address.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.get_caller_address.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.get_caller_address.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 3
                        },
                        "pc": 30,
                        "value": "[cast(fp + (-3), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 3
                        },
                        "pc": 33,
                        "value": "cast([fp + (-3)] + 2, felt*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.starknet.common.syscalls.get_contract_address": {
                "decorators": [],
                "pc": 37,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.get_contract_address.Args": {
                "full_name": "starkware.starknet.common.syscalls.get_contract_address.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_contract_address.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.get_contract_address.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_contract_address.Return": {
                "cairo_type": "(contract_address: felt)",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.get_contract_address.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.get_contract_address.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.get_contract_address.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 4
                        },
                        "pc": 37,
                        "value": "[cast(fp + (-3), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 4
                        },
                        "pc": 40,
                        "value": "cast([fp + (-3)] + 2, felt*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.starknet.common.syscalls.get_tx_info": {
                "decorators": [],
                "pc": 60,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.get_tx_info.Args": {
                "full_name": "starkware.starknet.common.syscalls.get_tx_info.Args",
                "size": 0,
                "members": {},
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_tx_info.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.get_tx_info.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.get_tx_info.Return": {
                "cairo_type": "(tx_info: starkware.starknet.common.syscalls.TxInfo*)",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.get_tx_info.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.get_tx_info.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.get_tx_info.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 7
                        },
                        "pc": 60,
                        "value": "[cast(fp + (-3), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 7
                        },
                        "pc": 63,
                        "value": "cast([fp + (-3)] + 2, felt*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.starknet.common.syscalls.storage_read": {
                "decorators": [],
                "pc": 44,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.storage_read.Args": {
                "full_name": "starkware.starknet.common.syscalls.storage_read.Args",
                "size": 1,
                "members": {
                    "address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.storage_read.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.storage_read.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.storage_read.Return": {
                "cairo_type": "(value: felt)",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.storage_read.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.storage_read.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.storage_read.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 5
                        },
                        "pc": 44,
                        "value": "[cast(fp + (-4), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 5
                        },
                        "pc": 48,
                        "value": "cast([fp + (-4)] + 3, felt*)"
                    }
                ],
                "type": "reference"
            },
            "starkware.starknet.common.syscalls.storage_write": {
                "decorators": [],
                "pc": 52,
                "type": "function"
            },
            "starkware.starknet.common.syscalls.storage_write.Args": {
                "full_name": "starkware.starknet.common.syscalls.storage_write.Args",
                "size": 2,
                "members": {
                    "address": {
                        "offset": 0,
                        "cairo_type": "felt"
                    },
                    "value": {
                        "offset": 1,
                        "cairo_type": "felt"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.storage_write.ImplicitArgs": {
                "full_name": "starkware.starknet.common.syscalls.storage_write.ImplicitArgs",
                "size": 1,
                "members": {
                    "syscall_ptr": {
                        "offset": 0,
                        "cairo_type": "felt*"
                    }
                },
                "type": "struct"
            },
            "starkware.starknet.common.syscalls.storage_write.Return": {
                "cairo_type": "()",
                "type": "type_definition"
            },
            "starkware.starknet.common.syscalls.storage_write.SIZEOF_LOCALS": {
                "value": 0,
                "type": "const"
            },
            "starkware.starknet.common.syscalls.storage_write.syscall_ptr": {
                "cairo_type": "felt*",
                "full_name": "starkware.starknet.common.syscalls.storage_write.syscall_ptr",
                "references": [
                    {
                        "ap_tracking_data": {
                            "offset": 0,
                            "group": 6
                        },
                        "pc": 52,
                        "value": "[cast(fp + (-5), felt**)]"
                    },
                    {
                        "ap_tracking_data": {
                            "offset": 1,
                            "group": 6
                        },
                        "pc": 57,
                        "value": "cast([fp + (-5)] + 3, felt*)"
                    }
                ],
                "type": "reference"
            }
        },
        "main_scope": "__main__",
        "debug_info": null,
        "reference_manager": {
            "references": [
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 1
                    },
                    "pc": 3,
                    "value": "[cast(fp + (-3), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 3,
                        "group": 1
                    },
                    "pc": 10,
                    "value": "[cast(ap, felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 2
                    },
                    "pc": 18,
                    "value": "[cast(fp + (-7), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 3
                    },
                    "pc": 30,
                    "value": "[cast(fp + (-3), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 4
                    },
                    "pc": 37,
                    "value": "[cast(fp + (-3), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 5
                    },
                    "pc": 44,
                    "value": "[cast(fp + (-4), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 6
                    },
                    "pc": 52,
                    "value": "[cast(fp + (-5), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 7
                    },
                    "pc": 60,
                    "value": "[cast(fp + (-3), felt**)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 8
                    },
                    "pc": 67,
                    "value": "[cast(fp + (-4), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 8
                    },
                    "pc": 67,
                    "value": "[cast(fp + (-3), felt*)]"
                },
                {
                    "ap_tracking_data": {
                        "offset": 0,
                        "group": 8
                    },
                    "pc": 67,
                    "value": "[cast(fp + (-7), starkware.cairo.common.cairo_builtins.SignatureBuiltin**)]"
                }
            ]
        },
        "prime": "0x800000000000011000000000000000000000000000000000000000000000001",
        "builtins": [
            "pedersen",
            "range_check",
            "ecdsa",
            "bitwise"
        ],
        "compiler_version": "0.10.0"
    }
}
"""
