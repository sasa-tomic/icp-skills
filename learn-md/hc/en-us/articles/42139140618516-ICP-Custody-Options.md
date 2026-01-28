# ICP Custody Options

There are various options for ICP wallets and custody services. The following table shows who typically uses each option, how easy it is to operate, the general security profile (assuming correct setup), and examples. Use it as a quick overview before diving into detailed guides.

| Category | Typical users | Ease | Security | Examples |
| --- | --- | --- | --- | --- |
| On-chain / Web | Everyday use, newcomers | High | Medium | [OISY](https://oisy.com/), [NNS dapp](https://nns.ic0.app/)\*, [Stoic](https://www.stoicwallet.com/), [NFID](https://nfid.one/) |
| Mobile | Frequent on-the-go | High | Medium | [Plug](https://plugwallet.ooo/), [AstroX ME](https://astrox.me/), [AirGap](https://airgap.it/), [Trust Wallet](https://trustwallet.com/), [Klever](https://klever.io/en-us/crypto-wallet/icp-wallet), [Bity](https://www.bity.com/bity-wallet) |
| Browser extension / Desktop | DeFi users, desktop-first | High | Medium | [Plug (ext)](https://plugwallet.ooo/), [Bitfinity](https://wallet.bitfinity.network/), [MetaMask (MSQ)](https://snaps.metamask.io/snap/npm/fort-major/msq/), [Trust Wallet](https://trustwallet.com/blog/beginners-guide-to-icp), [Primevault\*](https://www.primevault.com/) |
| Hardware / Cold / Air-gapped | Long-term holders, security-focused | Low–Medium | High | [Ledger hardware\*](https://www.ledger.com/hardware-wallets), [Quill\*](https://github.com/dfinity/quill), [AirGap](https://airgap.it/), [Tangem](https://tangem.com/en/cryptocurrencies/internet-computer/) |
| Institutional custody | Funds, companies, treasuries | High | High (operational) | [ARCHIP](https://www.archip.ch/), [BitGo](https://www.bitgo.com/), [Ceffu](https://www.ceffu.com/), [Cobo](https://www.cobo.com/), [Coinbase](https://www.coinbase.com/custody), [Copper\*](https://copper.co/), [Cordial Systems](https://cordial.systems/), [DFNS](https://www.dfns.co/), [Primevault\*](https://www.primevault.com/), [Sygnum\*](https://www.sygnum.com/digital-asset-banking/internet-computer-icp/), [Taurus\*](https://www.taurushq.com/), [Zodia](https://www.zodia.io/) |

The options marked with (\*) faciliatate ICP token staking.

### Quick chooser

Use this guide to select the custody option that suits you best.

## Custody options with staking

Do you want to participate in ICP governance or stake via the NNS?

### Yes: I want full control

- Use the [**NNS dapp**](https://nns.ic0.app/)  (Web) — the canonical way to create/manage neurons, vote, and handle staking directly in your browser, or
- Advanced/offline:
  - [**Ledger hardware**](https://www.youtube.com/watch?v=0-nSOBC3bxE) + [**NNS dapp**](https://nns.ic0.app/) — sign on hardware and manage neurons in the NNS dapp.
  - [**Quill**](https://github.com/dfinity/quill) (offline CLI) — create and manage neurons, vote, and perform ledger actions with fully offline signing workflows, then broadcast from an online machine.
  - [**Seed + air-gapped machine**](/hc/en-us/articles/41523709355668) — combine with Quill for end-to-end offline staking and governance operations.

### Yes: I prefer managed operations

- Use an institutional custodian that supports ICP staking. Confirm availability and operating model (e.g., policy controls, approvals, reporting). Examples:  [**Copper**](https://copper.co/), [**Primevault**](https://www.primevault.com/)[, **Taurus**](https://www.taurushq.com/), [**Sygnum**](https://www.sygnum.com/digital-asset-banking/internet-computer-icp/).

## Custody options without staking

Do you want to hold ICP tokens but don't plan to stake?

### Yes: prefer someone else to hold the keys

- Choose [institutional custody](#institutional-custody) (audits, support, SLAs).
- If you instead want an exchange account (CEX), see:
  - [CoinMarketCap list of ICP exchanges](https://coinmarketcap.com/currencies/internet-computer/#Markets)
  - [CoinGecko list of ICP exchanges](https://www.coingecko.com/en/coins/internet-computer)

### Yes: prefer self-custody with maximum ease

The most convenient path is a web/on-chain wallet. Popular choices are [**OISY**](https://oisy.com/) (no install) and the [**NNS dapp**](https://nns.ic0.app/).

- Fast setup; minimal maintenance.
- Good for everyday balances and newcomers.
- Check required features (e.g., SNS support, multisig, token standards) before committing.

### Yes: prefer self-custody with maximum control

For tighter control and a smaller software attack surface, use hardware/cold workflows such as [Ledger](https://www.youtube.com/watch?v=0-nSOBC3bxE) (with [Ledger Wallet](https://shop.ledger.com/pages/ledger-wallet) for management interface) or [seed + air-gapped machines](/hc/en-us/articles/41523709355668) (with [Quill](https://github.com/dfinity/quill) to sign ledger transactions offline).

- Highest control; greatest responsibility for backups and recovery.
- Best for large/long-term holdings.
- Practice recovery and small test runs before moving significant funds.

## Risk & best practices

- **Backups:** Store seeds/recovery materials across two or more physically separate, offline locations.
- **Phishing hygiene:** Bookmark official URLs (e.g., NNS dapp); verify certificates and domain spelling.
- **Device health:** Keep firmware up-to-date (hardware wallets) and maintain clean OS/app environments (hot wallets).
- **Least privilege:** Use hotkeys / separate accounts for daily use; keep cold storage isolated.
- **Change control:** For teams/treasuries, enforce multi-approver or MPC policies where available.
- **Test first:** Do small transfers and dry-runs of recovery before high-value actions.
