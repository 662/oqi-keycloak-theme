<#-- Native error model/link guards retained from Keycloak 21.1.2 (Apache-2.0). -->
<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=false; section>
    <#if section = "header">
        <#if message.summary?contains('redirect_uri')>${msg("oqiInvalidRedirectTitle")}<#else>${kcSanitize(msg("errorTitle"))?no_esc}</#if>
    <#elseif section = "form">
        <div id="kc-error-message">
            <#if message.summary?contains('redirect_uri')>
                <p class="instruction">${msg("oqiInvalidRedirectHint")}</p>
                <details class="oqi-error-details"><summary>${msg("oqiErrorDetails")}</summary><p class="message-text">${kcSanitize(message.summary)?no_esc}</p></details>
            <#else>
                <p class="instruction message-text">${kcSanitize(message.summary)?no_esc}</p>
                <p class="instruction">${msg("oqiErrorHelp")}</p>
            </#if>
            <#if skipLink??><#else><#if client?? && client.baseUrl?has_content>
                <p><a id="backToApplication" href="${client.baseUrl}">${kcSanitize(msg("backToApplication"))?no_esc}</a></p>
            </#if></#if>
        </div>
    </#if>
</@layout.registrationLayout>
