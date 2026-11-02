import freemarker.template.Configuration;
import freemarker.template.Template;
import freemarker.core.HTMLOutputFormat;
import java.io.File;
import java.io.StringReader;
import java.io.StringWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

/** Parse overrides and verify branding with Keycloak 21.1.2's FreeMarker engine. */
public class ValidateTemplates {
    private static int brandCases = 0;

    private static void checkBrand(Template harness, Map<String, String> realm,
                                   Map<String, String> properties, String expected) throws Exception {
        var output = new StringWriter();
        harness.process(Map.of("realm", realm, "properties", properties), output);
        if (!output.toString().equals(expected)) {
            throw new AssertionError("Brand rendering mismatch: " + output + " != " + expected);
        }
        brandCases++;
    }

    public static void main(String[] args) throws Exception {
        Configuration cfg = new Configuration(Configuration.VERSION_2_3_31);
        cfg.setDefaultEncoding("UTF-8");
        cfg.setOutputFormat(HTMLOutputFormat.INSTANCE);
        cfg.setDirectoryForTemplateLoading(new File(args[0]));
        try (var paths = Files.list(Path.of(args[0]))) {
            for (var path : paths.filter(p -> p.toString().endsWith(".ftl")).sorted().toList()) {
                cfg.getTemplate(path.getFileName().toString());
                System.out.println("Parsed: " + path.getFileName());
            }
        }
        var harness = new Template("brand-check",
            new StringReader("<#import 'template.ftl' as theme>${theme.brandLabel(realm, properties)}"), cfg);
        var defaults = Map.of("oqiBrand", "OQI.ME");
        checkBrand(harness, Map.of("name", "home", "displayName", "家庭空间"), defaults, "家庭空间");
        // RealmBean returns the internal name, not null, for an unset Display name.
        checkBrand(harness, Map.of("name", "home", "displayName", "home"), defaults, "OQI.ME");
        checkBrand(harness, Map.of("name", "home"), defaults, "OQI.ME");
        checkBrand(harness, Map.of("name", "home", "displayName", "   "), defaults, "OQI.ME");
        checkBrand(harness, Map.of("name", "home"), Map.of("oqiBrand", "Fallback"), "Fallback");
        checkBrand(harness, Map.of("name", "home"), Map.of("oqiBrand", "  "), "OQI.ME");
        checkBrand(harness, Map.of("name", "home"), Map.of(), "OQI.ME");
        checkBrand(harness, Map.of("name", "home", "displayName", "Family & <Home>"), defaults,
            "Family &amp; &lt;Home&gt;");
        checkBrand(harness, Map.of("name", "oqi.me", "displayName", "OQI.ME"),
            Map.of("oqiBrand", "Fallback"), "OQI.ME");
        System.out.println("Passed " + brandCases + " brand precedence/escaping cases.");
    }
}
