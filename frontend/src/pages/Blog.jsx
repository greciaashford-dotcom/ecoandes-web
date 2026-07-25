import React from "react";
import { Link } from "react-router-dom";
import { BLOG_POSTS } from "../data/blogPosts";
import { Clock } from "lucide-react";

export default function Blog() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-14 sm:py-20" data-testid="blog-page">
      <div className="overline mb-3">Blog</div>
      <h1 className="font-heading text-4xl sm:text-5xl font-light leading-[1.05]">
        Historias del campo a tu cocina
      </h1>
      <p className="mt-4 text-ink-soft font-light text-base max-w-xl">
        Reflexiones, recetas y guías sobre los productos ecológicos más vendidos de Ecoandes.
      </p>

      <div className="mt-14 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10">
        {BLOG_POSTS.map((p, i) => (
          <Link
            to={`/blog/${p.slug}`}
            key={p.slug}
            data-testid={`blog-card-${p.slug}`}
            className="group bg-white border border-bone-200 rounded-2xl overflow-hidden hover-lift hover:border-sage-300 flex flex-col"
          >
            <div className="aspect-[4/3] overflow-hidden bg-bone-200">
              <img
                src={p.cover}
                alt={p.title}
                className="w-full h-full object-cover group-hover:scale-[1.06] transition-transform duration-700"
                loading={i < 3 ? "eager" : "lazy"}
              />
            </div>
            <div className="p-6 flex-1 flex flex-col">
              <div className="overline mb-3">{p.category}</div>
              <h3 className="font-heading text-xl font-light text-ink leading-snug min-h-[60px] transition-colors duration-200 group-hover:text-sage-700">
                {p.title}
              </h3>
              <p className="text-sm text-ink-soft mt-3 line-clamp-3 font-light leading-relaxed">
                {p.excerpt}
              </p>
              <div className="mt-5 pt-4 border-t border-bone-200 flex items-center justify-between text-xs text-ink-muted">
                <span>{new Date(p.date).toLocaleDateString("es-ES", { year: "numeric", month: "long", day: "numeric" })}</span>
                <span className="flex items-center gap-1.5"><Clock size={12} /> {p.read_time}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
