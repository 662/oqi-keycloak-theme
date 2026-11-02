# Changelog

## 1.1.1

- Read the top-left brand from the realm Display name when it differs from the internal realm name.
- Fall back to `oqiBrand` (default `OQI.ME`) for the Keycloak 21.1 default name, missing names, or blank names.
- Render display names as escaped plain text and truncate long labels without breaking the layout.
- Test branding precedence and HTML escaping with the real FreeMarker engine.

## 1.1.0

First public release of the OQI.ME theme.

- Publish the `oqi` Keycloak 21.1 login theme with Chinese and English messages.
- Add OQI.ME branding and an `oqi.me` wooden nameplate to the watercolor cottage.
- Support responsive layouts, light/dark appearance and password visibility controls.
- Preserve native server-driven forms, errors, recovery, OTP, consent and logout behavior.
- Provide a Python-only JAR builder, installation documentation and validation notes.
