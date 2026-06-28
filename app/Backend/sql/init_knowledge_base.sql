-- =============================================================================
-- NeuroCap — Knowledge Base RAG (pgvector)
-- =============================================================================
-- À exécuter UNE SEULE FOIS dans Supabase SQL Editor :
-- https://supabase.com/dashboard/project/_/sql/new
--
-- Ordre d'exécution :
--   1. Extension pgvector
--   2. Table knowledge_documents
--   3. Index HNSW (similarité cosinus)
--   4. Fonction RPC match_documents
-- =============================================================================


-- ── 1. Activer l'extension pgvector ──────────────────────────────────────────
-- Fournit le type "vector" et les opérateurs de distance (<=> cosinus, <-> L2)
create extension if not exists vector
  with schema extensions;


-- ── 2. Table de la base de connaissances ─────────────────────────────────────
-- Chaque ligne = 1 document EEG/neurofeedback avec son embedding vectoriel
create table if not exists knowledge_documents (
  id          bigserial   primary key,
  title       text        not null unique,
  content     text        not null,
  category    text,                             -- 'eeg_basics' | 'concentration' | 'stress' | 'adaptation'
  embedding   vector(768),                      -- nomic-embed-text produit 768 dimensions
  created_at  timestamptz not null default now()
);

-- Commentaires de colonnes (optionnel mais utile)
comment on table  knowledge_documents           is 'Base de connaissances EEG/neurofeedback pour le RAG NeuroCoach';
comment on column knowledge_documents.embedding is 'Vecteur 768d produit par nomic-embed-text via Ollama';


-- ── 3. Index HNSW pour la recherche vectorielle rapide ───────────────────────
-- HNSW (Hierarchical Navigable Small World) :
--   - Fonctionne sur n'importe quelle taille de dataset (pas de minimum comme IVFFlat)
--   - Recherche approximative ultra-rapide (quelques ms même sur des millions de vecteurs)
--   - vector_cosine_ops → distance cosinus (1 - similarité cosinus)
create index if not exists knowledge_documents_embedding_idx
  on knowledge_documents
  using hnsw (embedding vector_cosine_ops)
  with (
    m              = 16,    -- nombre de liens par nœud (précision vs mémoire)
    ef_construction = 64    -- candidats évalués à la construction (précision)
  );


-- ── 4. Fonction RPC de recherche sémantique ──────────────────────────────────
-- Appelée depuis Python via : db.rpc("match_documents", {...}).execute()
--
-- Paramètres :
--   query_embedding  → vecteur 768d de la question utilisateur
--   match_threshold  → similarité cosinus minimum (0.0 – 1.0), défaut 0.5
--   match_count      → nombre maximum de résultats, défaut 5
--
-- Retourne les documents triés par pertinence décroissante
create or replace function match_documents(
  query_embedding  vector(768),
  match_threshold  float  default 0.50,
  match_count      int    default 5
)
returns table (
  id          bigint,
  title       text,
  content     text,
  category    text,
  similarity  float
)
language sql
stable                         -- lecture seule, même résultat pour mêmes args dans la transaction
security definer               -- s'exécute avec les droits du propriétaire de la fonction
as $$
  select
    id,
    title,
    content,
    category,
    -- similarité cosinus = 1 − distance cosinus
    -- distance cosinus (<=>)  : 0 = identiques, 2 = opposés
    -- similarité cosinus      : 1 = identiques, -1 = opposés
    (1 - (embedding <=> query_embedding))::float as similarity
  from knowledge_documents
  where (1 - (embedding <=> query_embedding)) > match_threshold
  order by embedding <=> query_embedding   -- tri ascendant par distance = descendant par similarité
  limit match_count;
$$;

-- Accorder l'exécution aux rôles authentifiés et anonymes
grant execute on function match_documents(vector, float, int)
  to authenticated, anon, service_role;


-- ── Vérification finale ───────────────────────────────────────────────────────
-- Après exécution, ce SELECT doit retourner 1 ligne
select
  'knowledge_documents' as table_name,
  (select count(*) from knowledge_documents) as nb_documents,
  'match_documents'     as rpc_function,
  'OK — exécutez maintenant scripts/init_kb.py' as next_step;
