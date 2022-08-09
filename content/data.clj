(ns ssgen.core
  (:require [clojure.java.shell]
            [clojure.java.io]))

(defn today [] (new java.util.Date))

(defn pandoc [template]
  (:out (clojure.java.shell/sh "pandoc" :in template :out-enc "UTF-8")))

(def sam {:name "Samuel Grayson"
          :bio (slurp (clojure.java.io/file "content" "bio.txt"))
          :url "https://samgrayson.me"
          :twitter "charmonium"})

(def nighthawks {:alt "A painting of The Nighthawks by Edward Hopper"
                 :url "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg"
                 :caption "A cool picture"
                 :attribution {:text "The Nighthawks by Edward Hopper (1942)"
                               :attrib_url "https://en.wikipedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg"}})

(def cc-by {:name "Creative Commons Attribution 4.0 International License"
            :url "http://creativecommons.org/licenses/by/4.0/"})

(def site {:name "Akademio"
           :twitter "charmoniumQ"
           :author sam
           :url "https://samgrayson.me"
           :root ""
           :nav [{:url "/blog" :text "Blog"}]})

{:output-dir (clojure.java.io/file "docs")
           :blog-posts [{:slug "illixr"
                         :title "ILLIXR: Illinois Extended Reality (AR/VR/MR) Testbed"
                         :image nighthawks
                         :teaser "I worked on ILLIXR."
                         :content (pandoc (slurp (clojure.java.io/file "content" "posts" "illixr.md")))}]
           :post-defaults {:license cc-by
                           :date-published (today)
                           :date-modified nil
                           :author sam
                           :language "en-US"
                           :content? true}
           :blog-meta {:title "Sam’s Blog"
                       :teaser "Sam’s Blog on computer science, math, history, and law."
                       :author sam
                       :image nighthawks
                       :language "en-US"
                       :content? true}
           :site site
           :not-found-page {:content (slurp "content/404.html")
                            :page {:title "Page not found"
                                   :content? false
                                   :language "en-US"}
                            :site site}}
