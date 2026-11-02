import freemarker.template.Configuration;
import freemarker.core.HTMLOutputFormat;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

/** Parse the overrides with the same FreeMarker version shipped by Keycloak 21.1.2. */
public class ValidateTemplates {
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
    }
}
