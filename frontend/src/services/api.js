const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000/api';
async function request(path,options){const r=await fetch(BASE+path,options);if(!r.ok){let d;try{d=await r.json()}catch{d={}};throw new Error(typeof d.detail==='string'?d.detail:'Request failed. Please try again.')}return r.status===204?null:r.json()}
export const api={projects:(query='')=>request('/projects'+query),project:id=>request(`/projects/${id}`),analysis:id=>request(`/analysis/${id}`),analyze:data=>request('/analysis',{method:'POST',body:data})};
