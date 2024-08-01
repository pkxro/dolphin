#!/bin/bash

# Install dependencies
sudo yum update -y
sudo yum install -y git

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Clone Solana repository
git clone https://github.com/solana-labs/solana.git
cd solana

# Build Solana
./scripts/cargo-install-all.sh .

# Add Solana to PATH
echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> $HOME/.bashrc
source $HOME/.bashrc

# Set up Solana CLI config
solana config set --url http://localhost:8899

# Create necessary keypairs
solana-keygen new --no-bip39-passphrase -o $HOME/solana-test-identity.json
solana-keygen new --no-bip39-passphrase -o $HOME/solana-test-vote.json
solana-keygen new --no-bip39-passphrase -o $HOME/solana-test-stake.json
solana-keygen new --no-bip39-passphrase -o $HOME/solana-test-authority.json

# Get public keys
IDENTITY_PUBKEY=$(solana-keygen pubkey $HOME/solana-test-identity.json)
VOTE_PUBKEY=$(solana-keygen pubkey $HOME/solana-test-vote.json)
STAKE_PUBKEY=$(solana-keygen pubkey $HOME/solana-test-stake.json)
AUTHORITY_PUBKEY=$(solana-keygen pubkey $HOME/solana-test-authority.json)

# Create genesis configuration
solana-genesis \
  --target-lamports-per-signature 0 \
  --target-signatures-per-slot 0 \
  --fee-burn-percentage 0 \
  --bootstrap-validator $IDENTITY_PUBKEY $VOTE_PUBKEY $STAKE_PUBKEY \
  --bootstrap-validator-stake-lamports 1000000000000 \
  --bootstrap-stake-authorized-pubkey $AUTHORITY_PUBKEY \
  --ledger $HOME/solana-test-ledger \
  --cluster-type development

# Start the validator
solana-validator \
  --identity $HOME/solana-test-identity.json \
  --vote-account $HOME/solana-test-vote.json \
  --ledger $HOME/solana-test-ledger \
  --gossip-port 8001 \
  --rpc-port 8899 \
  --rpc-faucet-address 127.0.0.1:9900 \
  --log - \
  --enable-rpc-transaction-history \
  --enable-cpi-and-log-storage \
  --init-complete-file /tmp/solana-init-complete \
  --snapshot-compression none \
  --accounts-db-caching-enabled \
  --no-snapshot-fetch \
  --no-genesis-fetch \
  --no-voting \
  --no-untrusted-rpc \
  --no-port-check \
  --full-rpc-api