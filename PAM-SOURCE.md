# pam — ONLYOFFICE custom marketplace

Based on https://github.com/ONLYOFFICE/onlyoffice.github.io
Upstream commit: 4d02c4fde76dd98b94129881a0d68366ae0e56e5

ONLYOFFICE Marketplace copyright Ascensio System SIA.
Upstream copyright, licence notices, logos and attributions are retained.
Runtime JavaScript, CSS and HTML sources are served unminified under /store/ and /sdkjs-plugins/v1/.
Third-party licence information: /store/3rd-Party.txt and /store/licenses/.
AI licence: /sdkjs-plugins/content/ai/LICENSE.txt.

pam modifications:
- The store/config.json catalogue contains only AI.
- The document title and sidebar identify the catalogue as pam.
- Store UI dependencies and connectivity checks use this host.
- Standalone downloads use the exact locally hosted official package.
- Indexing is discouraged with robots.txt and noindex headers/metadata.

AI 3.2.2 is extracted byte-for-byte from the unmodified official ai.plugin package.
Source: https://raw.githubusercontent.com/ONLYOFFICE/onlyoffice.github.io/master/sdkjs-plugins/content/ai/deploy/ai.plugin
SHA-256: 5e98cc51659cdf3fd0edcdf076137893575f4840a5fa6dcb2f460f93c8669c43
No AI plugin functionality or configuration has been changed.
