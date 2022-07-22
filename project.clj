(defproject ssgen "0.1.0-SNAPSHOT"
  :description "This is the configuration that generates my wesbsite."
  :url "http://github.com/charmoniumQ/samgrayson.me"
  :license {:name "MIT"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.10.3"]]
  :main ^:skip-aot ssgen.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all
                       :jvm-opts ["-Dclojure.compiler.direct-linking=true"]}})
