(let
    [output-dir "../docs"]
  [sam {
        :name "Samuel Grayson"
        :bio (slurp "bio.txt")
        :links {
                :homepage "https://samgrayson.me"
                :twitter "charmonium"
                :wikipedia "Charmoniumq"
                :github "charmoniumQ"}}]
  [nighthawks {
               :alt "A painting of The Nighthawks by Edward Hopper"
               :url "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg"
               :caption "A cool picture"
               :attribution {
                             :creator {
                                       :name "Edward Hopper"
                                       }
                             :date-published 1942
                             :license "public domain"
                             :attrib_url "https://en.wikipedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg"
                             }}]
  [blog-posts [
               {
                :slug "illixr"
                :title "ILLIXR: Illinois Extended Reality (AR/VR/MR) Testbed"
                :image nighthawks
                :teaser "I worked on ILLIXR."
                :content (pandoc (slurp "illixr.md"))}]]

  [post-defaults {
                  :license "http://creativecommons.org/licenses/by/4.0/"
                  :date-published (today)
                  :date-modified (today)
                  :author sam
                  :language en_US
                  }]
  [blog-index-page {
                    :title "Sam’s Blog"
                    :teaser "Sam’s Blog on computer science, math, history, and law."
                    :image nighthawks
                    }]
  [site {
         :name "Akademio"
         :twitter "charmoniumQ"
         :author sam
         :css "site.css"
         :url "https://samgrayson.me"}]
  (write-site
   output-dir
   (map
    (fn [page]
      (apply-template
       (get page :path)
       (slurp "site.html.jinja")
       :page (merge page-defaults page)
       :site site))

    (concat
     (apply-template2
      (slurp "blog_index.html.jinja")
      :posts blog-posts
      :page blog-index-page
      :path "blog/index.html")
     (map
      (fn [post] (let [post (merge post-defaults post)]
                   (apply-template2
                    (slurp "blog_post.html.jinja")
                    :post post
                    :page post
                    :path (str "blog/" (get post :slug)))))
      blog-posts)
     ))))
;(cider-clojure-cli-command)
