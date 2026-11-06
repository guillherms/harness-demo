// Copie para src/test/java/<seu/pacote>/arquitetura/ e ajuste os pacotes.
// Dependência no pom.xml (escopo test):
//   <dependency>
//     <groupId>com.tngtech.archunit</groupId>
//     <artifactId>archunit-junit5</artifactId>
//     <version>VERSÃO-APROVADA-NO-TIME</version>
//     <scope>test</scope>
//   </dependency>
//
// freeze(): na primeira execução grava as violações que JÁ existem (legado)
// em src/test/resources/archunit_store e só falha nas NOVAS. Commite o store.
// Habilite em src/test/resources/archunit.properties:
//   freeze.store.default.allowStoreCreation=true

package <seu.pacote>.arquitetura;

import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.library.Architectures.layeredArchitecture;
import static com.tngtech.archunit.library.freeze.FreezingArchRule.freeze;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

@AnalyzeClasses(packages = "<seu.pacote>")
class ArquiteturaTest {

    @ArchTest
    static final ArchRule camadas = freeze(
        layeredArchitecture().consideringOnlyDependenciesInLayers()
            .layer("Entrypoint").definedBy("..entrypoint..")
            .layer("Application").definedBy("..application..")
            .layer("Domain").definedBy("..domain..")
            .layer("Infrastructure").definedBy("..infrastructure..")
            .whereLayer("Entrypoint").mayNotBeAccessedByAnyLayer()
            .whereLayer("Application").mayOnlyBeAccessedByLayers("Entrypoint")
            .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Infrastructure")
    );

    @ArchTest
    static final ArchRule dominio_sem_spring = freeze(
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAPackage("org.springframework..")
    );
}
