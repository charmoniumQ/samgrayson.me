(ns ssgen.core
  (:require [clojure.java.shell]
            [selmer.parser]
            [stasis.core])
  (:gen-class))

(defn pandoc [template]
  (:out (clojure.java.shell/sh "pandoc" :in template :out-enc "UTF-8")))

(defn today [] (new java.util.Date))

(defn apply-template [template & {:as data}]
  (assoc data :content ( template data)))

(defn write-files [output-dir files]
  (.delete output-dir)
  (println "files" (.size files))
  (doseq
      [[path file] files]
    (let [path (.toFile (.resolve (.toPath output-dir) (.toPath path)))]
      (.mkdirs (.getParentFile path))
      (println "write" path "{")
      (spit path file)
      (println "}"))))

(selmer.filters/add-filter!
 :human-readable-date
 (fn [date]
   (.format
    (new java.text.SimpleDateFormat "yyyy LLLL d")
    date)))

(selmer.filters/add-filter!
 :iso-date
 (fn [date]
   (.format
    (new java.text.SimpleDateFormat "yyyy-MM-dd")
    date)))

(selmer.filters/add-filter!
 :replaceDashWithUnder
 (fn [html-string]
   (clojure.string/replace html-string "-"  "_")))

(selmer.filters/add-filter!
 :html2text
 (fn [html-string]
   (clojure.string/replace html-string #"<.*?>" "")))

(def
  server
  (let
      [output-dir (clojure.java.io/file "docs")
       sam {
            :name "Samuel Grayson"
            :bio (slurp (clojure.java.io/file "content" "bio.txt"))
            :links {
                    :homepage "https://samgrayson.me"
                    :twitter "charmonium"
                    :wikipedia "Charmoniumq"
                    :github "charmoniumQ"}}
       nighthawks {
                   :alt "A painting of The Nighthawks by Edward Hopper"
                   :url "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg"
                   :caption "A cool picture"
                   :attribution {:creator {:name "Edward Hopper"}
                                 :date-published 1942
                                 :license "public domain"
                                 :attrib_url "https://en.wikipedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg"}}
       
       blog-posts [{:slug "illixr"
                    :title "ILLIXR: Illinois Extended Reality (AR/VR/MR) Testbed"
                    :image nighthawks
                    :teaser "I worked on ILLIXR."
                    :content (pandoc (slurp (clojure.java.io/file "content" "posts" "illixr.md")))}]

       cc-by {:name "Creative Commons Attribution 4.0 International License"
              :url "http://creativecommons.org/licenses/by/4.0/"}
       post-defaults {:license cc-by
                      :date-published (today)
                      :date-modified (today)
                      :author sam
                      :language "en-US"}
       
       blog-index-page {:title "Sam’s Blog"
                        :teaser "Sam’s Blog on computer science, math, history, and law."
                        :image nighthawks
                        :language "en-US"}
       
       site {:name "Akademio"
             :twitter "charmoniumQ"
             :author sam
             :url "https://samgrayson.me"
             :root ""}
       page-template (slurp "content/page.html.jinja")]

    (stasis.core/serve-pages
     (merge

      {(clojure.java.io/file "/" "main.css") (slurp "content/main.css")}
                                        ; blog index

      (let [path (clojure.java.io/file "/" "blog" "index.html")]
        
        {path (selmer.parser/render
               page-template
               {
                :page blog-index-page
                :path path
                :content (selmer.parser/render
                          (slurp "content/blog_index.html.jinja")
                          {:posts (map
                                   (fn [post] (merge post-defaults post))
                                   blog-posts)})})})

                                        ; blog posts
      (apply
       merge
       (map
        (fn [post]
          (let [post (merge post-defaults post)
                path (clojure.java.io/file
                      "/"
                      "blog"
                      (str (:slug post) ".html"))
                page-content (selmer.parser/render
                              page-template
                              {:page post
                               :path path
                               :site site
                               :content (selmer.parser/render
                                         (slurp "content/blog_post.html.jinja")
                                         {:post post})})]
            {(str path) page-content}))
        blog-posts))))))
