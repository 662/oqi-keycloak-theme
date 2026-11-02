<#-- OQI.ME layout. Derived from Keycloak 21.1.2 template.ftl (Apache-2.0). -->
<#macro registrationLayout bodyClass="" displayInfo=false displayMessage=true displayRequiredFields=false>
<!DOCTYPE html>
<html class="${properties.kcHtmlClass!}" lang="${(locale.currentLanguageTag)!'en'}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">
    <#if properties.meta?has_content>
        <#list properties.meta?split(' ') as meta>
            <meta name="${meta?split('==')[0]}" content="${meta?split('==')[1]}"/>
        </#list>
    </#if>
    <title>${msg("oqiBrowserTitle")}</title>
    <link rel="icon" type="image/svg+xml" href="${url.resourcesPath}/img/favicon.svg" />
    <#if properties.stylesCommon?has_content>
        <#list properties.stylesCommon?split(' ') as style>
            <link href="${url.resourcesCommonPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.styles?has_content>
        <#list properties.styles?split(' ') as style>
            <link href="${url.resourcesPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.scripts?has_content>
        <#list properties.scripts?split(' ') as script>
            <script src="${url.resourcesPath}/${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <#if scripts??>
        <#list scripts as script>
            <script src="${script}" type="text/javascript"></script>
        </#list>
    </#if>

</head>
<body class="oqi-page ${properties.kcBodyClass!} ${bodyClass}" data-oqi-show-password="${msg('oqiShowPassword')}" data-oqi-hide-password="${msg('oqiHidePassword')}">
<main class="oqi-layout<#if (properties.oqiShowIllustration!'true') == 'false'> oqi-no-illustration</#if>">
    <section class="oqi-landscape" aria-label="${msg('oqiPrivateSpace')}">
        <div class="oqi-grain" aria-hidden="true"></div>
        <div class="oqi-brand"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M4 15 16 5l12 10v12H4V15Z" stroke="currentColor" stroke-width="1.8"/><path d="M11 27V14h10v13M16 14v13" stroke="currentColor" stroke-width="1.8"/></svg><span>${properties.oqiBrand!'OQI.ME'}</span><small>${msg('oqiBrandTagline')}</small></div>
        <img class="oqi-art" src="${url.resourcesPath}/img/home-oqi.png" alt="${msg('oqiIllustrationAlt')}" />
        <div class="oqi-intro"><div class="oqi-eyebrow">${msg('oqiEyebrow')}</div><h2>${msg('oqiHeadline')}</h2><p>${msg('oqiDescription')}</p></div>
        <div class="oqi-landscape-footer"><span>${msg('oqiPersonalCloud')}</span><span><i class="oqi-dot" aria-hidden="true"></i>${msg('oqiMadeForYou')}</span></div>
    </section>
    <section class="oqi-login-side">
        <div class="oqi-topbar">
            <#if realm.internationalizationEnabled && locale.supported?size gt 1>
                <details class="oqi-locale" id="kc-locale"><summary aria-label="${msg('oqiChooseLanguage')}">${locale.current}</summary><ul>
                    <#list locale.supported as l><li><a href="${l.url}">${l.label}</a></li></#list>
                </ul></details>
            </#if>
            <button type="button" class="oqi-theme-toggle" id="oqi-theme-toggle" aria-label="${msg('oqiToggleTheme')}" aria-pressed="false" hidden><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/></svg></button>
        </div>
        <div class="oqi-form-wrap" id="kc-form-card">
            <div class="oqi-entry-icon<#if message?has_content && message.type == 'error'> oqi-state-error<#elseif message?has_content && message.type == 'warning'> oqi-state-warning<#elseif message?has_content && message.type == 'success'> oqi-state-success</#if>" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
                    <#if message?has_content && message.type == 'error'><circle cx="12" cy="12" r="9"/><path d="m9 9 6 6m0-6-6 6"/>
                    <#elseif message?has_content && message.type == 'warning'><path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3v1"/>
                    <#elseif message?has_content && message.type == 'success'><circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>
                    <#else><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/></#if>
                </svg>
            </div>
            <header class="oqi-form-header">
        <#if !(auth?has_content && auth.showUsername() && !auth.showResetCredentials())>
            <#if displayRequiredFields>
                <div class="${properties.kcContentWrapperClass!}">
                    <div class="${properties.kcLabelWrapperClass!} subtitle">
                        <span class="subtitle"><span class="required">*</span> ${msg("requiredFields")}</span>
                    </div>
                    <div class="col-md-10">
                        <h1 id="kc-page-title"><#nested "header"></h1>
                    </div>
                </div>
            <#else>
                <h1 id="kc-page-title"><#nested "header"></h1>
            </#if>
        <#else>
            <#if displayRequiredFields>
                <div class="${properties.kcContentWrapperClass!}">
                    <div class="${properties.kcLabelWrapperClass!} subtitle">
                        <span class="subtitle"><span class="required">*</span> ${msg("requiredFields")}</span>
                    </div>
                    <div class="col-md-10">
                        <h1 id="kc-page-title">${msg("oqiContinueTitle")}</h1>
                        <#nested "show-username">
                        <div id="kc-username" class="${properties.kcFormGroupClass!}">
                            <label id="kc-attempted-username">${auth.attemptedUsername}</label>
                            <a id="reset-login" href="${url.loginRestartFlowUrl}" aria-label="${msg("restartLoginTooltip")}">
                                <div class="kc-login-tooltip">
                                    <i class="${properties.kcResetFlowIcon!}"></i>
                                    <span class="kc-tooltip-text">${msg("restartLoginTooltip")}</span>
                                </div>
                            </a>
                        </div>
                    </div>
                </div>
            <#else>
                <h1 id="kc-page-title">${msg("oqiContinueTitle")}</h1>
                        <#nested "show-username">
                <div id="kc-username" class="${properties.kcFormGroupClass!}">
                    <label id="kc-attempted-username">${auth.attemptedUsername}</label>
                    <a id="reset-login" href="${url.loginRestartFlowUrl}" aria-label="${msg("restartLoginTooltip")}">
                        <div class="kc-login-tooltip">
                            <i class="${properties.kcResetFlowIcon!}"></i>
                            <span class="kc-tooltip-text">${msg("restartLoginTooltip")}</span>
                        </div>
                    </a>
                </div>
            </#if>
        </#if>

            </header>
            <div id="kc-content"><div id="kc-content-wrapper">
          <#-- App-initiated actions should not see warning messages about the need to complete the action -->
          <#-- during login.                                                                               -->
          <#if displayMessage && message?has_content && (message.type != 'warning' || !isAppInitiatedAction??)>
              <div class="alert-${message.type} ${properties.kcAlertClass!} pf-m-<#if message.type = 'error'>danger<#else>${message.type}</#if>">
                  <div class="pf-c-alert__icon" aria-hidden="true">
                      <#if message.type = 'success'><span class="${properties.kcFeedbackSuccessIcon!}"></span></#if>
                      <#if message.type = 'warning'><span class="${properties.kcFeedbackWarningIcon!}"></span></#if>
                      <#if message.type = 'error'><span class="${properties.kcFeedbackErrorIcon!}"></span></#if>
                      <#if message.type = 'info'><span class="${properties.kcFeedbackInfoIcon!}"></span></#if>
                  </div>
                      <span role="status" aria-live="polite" class="${properties.kcAlertTitleClass!}">${kcSanitize(message.summary)?no_esc}</span>
              </div>
          </#if>

          <#nested "form">

          <#if auth?has_content && auth.showTryAnotherWayLink()>
              <form id="kc-select-try-another-way-form" action="${url.loginAction}" method="post">
                  <div class="${properties.kcFormGroupClass!}">
                      <input type="hidden" name="tryAnotherWay" value="on"/>
                      <button type="submit" id="try-another-way" class="oqi-link-button">${msg("doTryAnotherWay")}</button>
                  </div>
              </form>
          </#if>

          <#nested "socialProviders">

          <#if displayInfo>
              <div id="kc-info" class="${properties.kcSignUpClass!}">
                  <div id="kc-info-wrapper" class="${properties.kcInfoAreaWrapperClass!}">
                      <#nested "info">
                  </div>
              </div>
          </#if>

            </div></div>
            <div class="oqi-private-note"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="m12 3 8 4v5c0 5-8 9-8 9s-8-4-8-9V7l8-4Z"/><path d="m8 12 3 3 5-6"/></svg><span>${msg('oqiPrivacyNote')}</span></div>
        </div>
        <footer class="oqi-footer">${msg('oqiFooter')}</footer>
    </section>
</main>
</body>
</html>
</#macro>
