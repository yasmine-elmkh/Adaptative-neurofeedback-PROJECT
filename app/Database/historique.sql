-- Récupérer l'historique complet d'un utilisateur
SELECT 
    s.session_number,
    s.objective,
    s.session_score,
    s.success_rate,
    s.avg_tbr,
    s.created_at
FROM sessions s
WHERE s.user_id = $1
ORDER BY s.session_number ASC;


-- Comparer les performances entre deux sessions
SELECT 
    s1.session_number as session_1,
    s1.session_score as score_1,
    s1.avg_tbr as tbr_1,
    s2.session_number as session_2,
    s2.session_score as score_2,
    s2.avg_tbr as tbr_2,
    ((s2.session_score - s1.session_score) / s1.session_score * 100) as improvement_pct
FROM sessions s1
JOIN sessions s2 ON s1.user_id = s2.user_id 
    AND s2.session_number = s1.session_number + 1
WHERE s1.user_id = $1;


-- Trouver les utilisateurs avec progression rapide
SELECT 
    u.id,
    u.email,
    COUNT(s.id) as sessions_count,
    AVG(s.session_score) as avg_score,
    STDDEV(s.session_score) as score_stability
FROM users u
JOIN sessions s ON u.id = s.user_id
WHERE s.created_at > NOW() - INTERVAL '4 weeks'
GROUP BY u.id
HAVING COUNT(s.id) >= 10
ORDER BY avg_score DESC;