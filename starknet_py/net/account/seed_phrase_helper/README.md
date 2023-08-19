Ethereum BIP44 Python
================================

*Code adapted from two1 library for bitcoin by 21 Inc. (https://github.com/21dotco/two1-python/tree/master/two1)

### Requirements
Python packages:  
`pip install -r requirements.txt`

Imports:  
`from crypto import HDPrivateKey, HDPublicKey, HDKey`

### BIP32 Master Keys Creation:
```
master_key, mnemonic = HDPrivateKey.master_key_from_entropy()
print('BIP32 Wallet Generated.')  
print('Mnemonic Secret: ' + mnemonic)
```

### Accounts creation
Creation of multiple accounts under master key derived from seed phrase.
Compatible with [Metamask](https://metamask.io). You can just restore your wallet 
with seed phrase and get access to all the accounts under master key via Metamask.
```
from crypto import HDPrivateKey, HDKey
master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy finger bone real west arch protect')
root_keys = HDKey.from_path(master_key,"m/44'/60'/0'")
acct_priv_key = root_keys[-1]
for i in range(10):
    keys = HDKey.from_path(acct_priv_key,'{change}/{index}'.format(change=0, index=i))
    private_key = keys[-1]
    public_key = private_key.public_key
    print("Index %s:" % i)
    print("  Private key (hex, compressed): " + private_key._key.to_hex())
    print("  Address: " + private_key.public_key.address())
```

### Get Account XPUB
```
master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy finger bone real west arch protect')
root_keys = HDKey.from_path(master_key,"m/44'/60'/0'")
acct_priv_key = root_keys[-1]
acct_pub_key = acct_priv_key.public_key
print('Account Master Public Key (Hex): ' + acct_pub_key.to_hex())
print('XPUB format: ' + acct_pub_key.to_b58check())
```

### Get Address from XPUB
```
acct_pub_key = HDKey.from_b58check('xpub6DKMR7KpgCJbiN4TdzcqcB1Nk84D9bsYUBhbk43EjRqH4RTjz7UgGLZxcQ4JdHBSHDmTUDLApMwYHRQCbbMCPQEtcbVofZEQjFazpGPT1nW')
keys = HDKey.from_path(acct_pub_key,'{change}/{index}'.format(change=0, index=0))
address = keys[-1].address()
print('Account address: ' + address)
```
### Get 64 Character Private Key from XPRIV
```
print(Private key (hex): " + private_key._key.to_hex())

```





