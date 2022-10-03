(ns ssgen.core
  (:require [clojure.java.shell]
            [clj-yaml.core]
            [clojure.string]
            [clojure.java.io]))

(defn today [] (new java.util.Date))

(defn pandoc [document]
  (:out (clojure.java.shell/sh "pandoc" :in document :out-enc "UTF-8")))

(defn parse-yaml-markdown [path]
  (let [contents (clojure.string/split (slurp path) #"---" 3)]
    (merge
     (clj-yaml.core/parse-string (second contents))
     {:content (pandoc (get contents 2))
      :slug (first
             (clojure.string/split
              (.getName path)
              #"\."))})))

(def sam {:name "Samuel Grayson"
          :url "https://samgrayson.me"
          :twitter "charmonium"})

(def nighthawks {:alt "A painting of The Nighthawks by Edward Hopper"
                 :url "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg"
                 :caption "A cool picture"
                 :attribution {:text "The Nighthawks by Edward Hopper (1942)"
                               :attrib_url "https://en.wikipedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg"}})

(def cc-by {:name "Creative Commons Attribution 4.0 International License"
            :url "http://creativecommons.org/licenses/by/4.0/"})

(def site {:name "Samuel Grayson"
           :twitter "charmoniumQ"
           :author sam
           :url "https://samgrayson.me"
           :root ""
           :favicon (clojure.java.io/file "content" "raw-text" "favicon.svg")
           :nav [{:url "/essays" :text "Essays"}
                 ;; {:url "/cv.html" :text "CV"}
                 {:url "https://scholar.google.com/citations?user=EEOIkYEAAAAJ&hl=en", :text "Publications"}]})
                 

{:output-dir (clojure.java.io/file "docs")
 :blog-posts (reverse
              (sort-by
               (fn [post] (:date-published post))
               (map
                parse-yaml-markdown
                (filter
                 (fn [file] (.isFile file))
                 (file-seq (clojure.java.io/file "content/posts"))))))
 :post-defaults {:license cc-by
                 :date-published (today)
                 :date-modified nil
                 :author sam
                 :language "en-US"
                 :content? true}
 :blog-meta {:title "Essays"
             :teaser "Sam’s essays on computer science, math, history, language, and law."
             :author sam
             :image nighthawks
             :language "en-US"
             :content? true}
 :site site
 :not-found-page {:content (slurp "content/404.html")
                  :page {:title "Page not found"
                         :content? false
                         :language "en-US"}
                  :site site}
 :front-page {:content (slurp "content/front_page.html")
              :path "/"
              :page {:title "Samuel Grayson"
                     :teaser "Samuel Grayson’s site"
                     :content? true
                     :language "en-US"
                     :image {:url "/raw-binary/self.jpg"
                             :alt "Samuel Grayson"}}
              :site site}}
