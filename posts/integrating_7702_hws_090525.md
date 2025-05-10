[category]: <> (General)
[date]: <> (2025/05/09)
[title]: <> (Integrating EIP-7702 with Hardware Wallets)

<p align="center">
<img src="../../../../../images/pectra7702hws.jpeg" alt="pektra" class="center"/>
<p align="center">
<small>(Pectra adding support for Hardware Wallets)</small>

## Introduction

We've illustrated in a previous blog post [how Hardware Wallet vendors could use [EIP-7702](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7702.md) quickly and efficiently](https://zknox.eth.limo/posts/2025/05/07/7702_for_hw_070525.html). We'll now take a different perspective and see how a wallet vendor could integrate a Hardware Wallet supporting EIP-7702 today. 

Support scope and data flow is different from one vendor to another, but they'll be offering the same functionalities from a high level point of view : signing an EIP-7702 authorization tuple and a type 4 transaction. It's expected that delegate addresses will be filtered for security purposes.

We'll be looking at 3 Hardware Wallet vendors : [Keystone](https://keyst.one/), [Ledger](https://www.ledger.com) and [Trezor](https://trezor.io)

Note that at the moment EIP-7702 is only officially supported for Ledger devices. Data parameters and flow for other vendors may change as the Pull Requests evolve. 

## Ledger support 

### Overview

EIP-7702 support is officially available for all Ledger devices (X, S+, Stax, Flex) but the Nano S. It could be easily backported if desired.

The Ethereum application running on devices is available at https://github.com/LedgerHQ/app-ethereum

### EIP-7702 authorization tuple signing flow

The following parameters are provided when signing an EIP-7702 authorization tuple

- BIP-32 path to the key signing the authorization tuple
- Delegate address
- Chain ID
- Nonce

The device verifies that the delegate is in the application whitelist, displays all parameters related to the authorization tuple, asks the user for confirmation and returns the authorization tuple signature (```v, r, s``` fields) 

### TX type 4 signing flow

The device expects an unsigned Type 4 transaction containing an authorization list. After confirmation of the different transaction elements the device returns the transaction signature (```v, r, s``` fields). The authorization list is not displayed to the user. 

### I/O documentation

The parameters for the ```SIGN EIP-7702 AUTHORIZATION``` command are described in https://github.com/LedgerHQ/app-ethereum/blob/develop/doc/ethapp.adoc#sign-eip-7702-authorization

The ```AUTH_7702``` structure uses a DER (Distinguished Encoding Rules) TLV (Tag/Length/Value) encoding which can be summarized as follows for this use case : 

The DER encoding of an integer smaller than 0x7F is the integer.

The DER encoding of an integer greater than 0x7F is 0x8X where X is the number of bytes of the smallest representation of the integer, followed by the smallest representation of the integer in big endian notation. For example ```0x80``` will be DER encoded as ```0x81 0x80```.

A DER TLV is encoded as the DER encoding of the tag, concatenated with the DER encoding of the length, followed by the value.

### Building the device application

You'll need to rebuild the application if you're testing an EIP-7702 delegate that isn't in the [whitelist](https://github.com/LedgerHQ/app-ethereum/blob/develop/src_features/signAuthorizationEIP7702/whitelist_7702.c) for the current version loaded by Ledger Live.

The device application can be rebuilt and side loaded on any device following the instructions given on https://github.com/LedgerHQ/app-ethereum/blob/develop/README.md - it's recommended to use a Linux system and Docker from the CLI.

If you're not comfortable with running Docker in privileged mode, you can remove it, use the container to build the application then load it from your OS.

To test a new delegate address you can either add it to the [whitelist](https://github.com/LedgerHQ/app-ethereum/blob/develop/src_features/signAuthorizationEIP7702/whitelist_7702.c) or remove the ```HAVE_EIP7702_WHITELIST``` feature from the [Makefile](https://github.com/LedgerHQ/app-ethereum/blob/develop/makefile_conf/features.mk).

### Integrating the client

EIP-7702 support will be ultimately integrated into Ledger new client architecture, the [Device Management Kit](https://github.com/LedgerHQ/device-sdk-ts) - it's recommended for all integrators to switch to this client to support all clear signing features.

In the meantime for a faster integration you can use the former client, ```@ledgerhq/hw-app-eth``` (https://github.com/LedgerHQ/ledger-live/tree/develop/libs/ledgerjs/packages/hw-app-eth)

The [client](https://github.com/LedgerHQ/ledger-live/blob/develop/libs/ledgerjs/packages/hw-app-eth/src/Eth.ts) will need to be modified to add support for the ```SIGN EIP-7702 AUTHORIZATION``` command.

You can get some inspiration from this [sample Python script](https://github.com/LedgerHQ/app-ethereum/blob/develop/examples/signAuthorizationEIP7702.py).

## Keystone support 

### Overview

EIP-7702 support is avaiable in [PR #1727 for the firmware](https://github.com/KeystoneHQ/keystone3-firmware/pull/1727) and [PR #112 for the SDK](https://github.com/KeystoneHQ/keystone-sdk-rust/pull/112)

### EIP-7702 authorization tuple signing flow

The EIP-7702 authorization tuple is RLP encoded without the ```y_parity, r, s``` fields, along with the path to the key signing the authorization, into a QR code that can be scanned by the device. When scanned, the device displays all parameters related to the authorization tuple, asks the user for confirmation and returns the authorization tuple signature (```y_parity, r, s``` fields) as a QR code that can be scanned by the client. 

### TX type 4 signing flow

The device expects an unsigned Type 4 transaction containing an authorization list encoded into a dedicated animated QR code, along with a path to the key signing this transaction. After confirmation of the different transaction elements the device returns the transaction signature (```y_parity, r, s``` fields) as a QR code that can be scanned by the client. The authorization list is not displayed to the user. 

### I/O documentation

You can reuse [the following code sample](https://github.com/KeystoneHQ/keystone-sdk-base/blob/master/packages/ur-registry-eth/__tests__/EthSignRequest.test.ts) to generate the content of the QR code to sign an EIP-7702 authorization tuple with some modifications :

- run the code independently by importing ```@keystonehq/bc-ur-registry-eth``` instead of importing from ```../src```
- set the RLP encoded unsigned authorization tuple ```[chain_id, address, nonce]``` as ```rlpData```
- modify the master fingerprint in ```signKeyPath``` by the one of your mnemonic
- set ```dataType``` to 5 in ```ethSignRequest``` 

The response encoded as an ```EthSignature``` UR can be decoded with [the following code sample](https://github.com/KeystoneHQ/keystone-sdk-base/blob/master/packages/ur-registry-eth/__tests__/EthSignature.test.ts)

### Building the device application

There's no official way to run a modified firmware on your device. If you're running a version with an older firmware (version 1.2.2 or 1.2.4) you might be able to use an exploit to do it nonetheless - see [ks3-devkit](https://github.com/ZKNoxHQ/ks3-devkit)

In that case, you can build the [```auth_7702``` branch](https://github.com/btchip/keystone3-firmware/tree/auth_7702) as described in the [README.md](https://github.com/btchip/keystone3-firmware/blob/auth_7702/README.md)

After building, you can sign the firmware with [signFirmware.py](https://github.com/ZKNoxHQ/ks3-devkit/blob/main/signFirmware.py) or [signFirmwareOta2.py](https://github.com/ZKNoxHQ/ks3-devkit/blob/main/signFirmwareOta2.py) if you updated the bootloader with firmware 2.0.4 - using the private key associated to the public key you injected earlier with [setUpdateKey.py](https://github.com/ZKNoxHQ/ks3-devkit/blob/main/setUpdateKey.py)

You can then load the firmware either with [uploadFirmware.py](https://github.com/ZKNoxHQ/ks3-devkit/blob/main/uploadFirmware.py), or rename it ```keystone3.bin``` and put it on a SD card or use the [Recovery Mode](https://keystonewallet.crisp.help/en/article/my-keystone-3-pro-cannot-turn-on-1e0c2p2/) 

### Integrating the client

You can refer to the [web SDK demonstration](https://github.com/KeystoneHQ/keystone-sdk-web-demo) or the [USB SDK](https://github.com/KeystoneHQ/keystone-sdk-usb) - you'll need to support a new ```DataType``` as described in the I/O chapter

## Trezor support 

### Overview

EIP-7702 support is avaiable in [PR #4945 for the firmware](https://github.com/trezor/trezor-firmware/pull/4945) for Trezor T, Trezor Safe 3 and Trezor Safe 5.


### EIP-7702 authorization tuple signing flow

New [Protocol Buffers](https://github.com/btchip/trezor-firmware/blob/main/common/protob/messages-ethereum.proto) messages ```EthereumSignAuth7702``` and ```EthereumAuth7702Signature``` are introduced to support EIP-7702 authorization tuple signing.

When receiving an ```EthereumSignAuth7702``` message, the device will display the ```delegate```, ```nonce``` and ```chain_id```, asks the user for confirmation and returns the authorization tuple signature as an ```EthereumAuth7702Signature``` message in ```signature_v```, ```signature_r``` and ```signature_s```

### TX type 4 signing flow

A new Protocol Buffers message ```EthereumSignedAuth7702``` is introduced in the ```EthereumSignTx``` message to add the EIP-7702 authorization list, containing all elements of the authentication tuple (```chain_id```, ```delegate```, ```nonce```, ```signature_v```, ```signature_r```, ```signature_s```)

When receiving an ```EthereumSignTx``` message containing an ```EthereumSignedAuth7702```, the device will handle it as a Type 4 transaction. After confirmation of the different transaction elements the device returns the transaction signature in a ```EthereumTxRequest``` message (```signature_v```, ```signature_r```, ```signature_s```). The authorization list is not displayed to the user.

### I/O documentation

I/O parameters are self described by the Protocol Buffers messages

### Building the device application

Follow the [documentation](https://docs.trezor.io/trezor-firmware/core/build/embedded.html) to build the firmware and load it on a device. Note that this operation turns definitely the device into a developer unit for Trezor Safe 3 and 5.

### Integrating the client

You can use the modified Protocol Buffer definitions with your existing client.

You can also directly try the EIP-7702 functionalities from the CLI with ```trezorctl eth sign-auth-7702``` and ```trezorctl eth sign-tx``` with the ```--auth-list``` parameter