import { Box, Typography, Paper, Divider } from '@mui/material';

export default function TransparenciaPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Transparência no Cálculo de Impacto
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Como o Impacto é Calculado?
        </Typography>
        <Typography variant="body1" paragraph>
          O "Score de Impacto" de cada proposição legislativa é uma métrica que busca estimar a sua relevância política e social. O cálculo é realizado por um sistema de Inteligência Artificial que analisa diversas dimensões da proposta para gerar uma pontuação final.
        </Typography>
        <Typography variant="body1" paragraph>
          Este sistema é composto por duas partes principais: uma análise qualitativa feita por um Modelo de Linguagem Grande (LLM) e uma fórmula de cálculo que pondera os resultados da IA com dados estruturados da própria proposição.
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          A Fórmula do Score de Impacto
        </Typography>
        <Typography variant="body1" paragraph>
          O score final é calculado utilizando a seguinte fórmula, que pode ser encontrada no arquivo <strong>backend/app/services/scoring_service.py</strong>:
        </Typography>
        <Paper component="pre" variant="outlined" sx={{ p: 2, backgroundColor: 'grey.100', overflowX: 'auto', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
          <code>
            Score = (Peso da Abrangência) + (Peso da Magnitude) + (Estimativa do LLM) + (Bônus para PEC)
          </code>
        </Paper>
        <Typography variant="body1" paragraph sx={{ mt: 2 }}>
          Os pesos atribuídos a cada critério são:
        </Typography>
        <ul>
          <li><strong>Peso da Abrangência (scope_weights)</strong>
            <ul>
              <li>Nacional: <strong>35</strong></li>
              <li>Estadual: <strong>15</strong></li>
              <li>Municipal: <strong>5</strong></li>
            </ul>
          </li>
          <li><strong>Peso da Magnitude (magnitude_weights)</strong>
            <ul>
              <li>População Geral: <strong>25</strong></li>
              <li>Setorial Específico: <strong>15</strong></li>
              <li>Alto: <strong>10</strong></li>
              <li>Médio: <strong>5</strong></li>
              <li>Baixo: <strong>5</strong></li>
            </ul>
          </li>
          <li><strong>Estimativa do LLM (llm_impact_estimate)</strong>
            <ul>
              <li>Um valor de <strong>0 a 30</strong> atribuído diretamente pelo modelo de IA.</li>
            </ul>
          </li>
          <li><strong>Bônus para PEC (Proposta de Emenda à Constituição)</strong>
            <ul>
              <li>Se a proposição for uma PEC, um bônus de <strong>10</strong> pontos é adicionado.</li>
            </ul>
          </li>
        </ul>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          O score final é limitado a um máximo de 100 pontos.
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Prompt Utilizado no LLM
        </Typography>
        <Typography variant="body1" paragraph>
          Este é o prompt exato, extraído do arquivo <strong>backend/prompts/analyze_proposition_prompt.txt</strong>, que nosso sistema utiliza para instruir o modelo de IA a analisar a ementa de cada proposição.
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.100', overflowX: 'auto' }}>
          <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.875rem', margin: 0 }}>
            <code>
{`Você é um analista legislativo com profundo conhecimento da legislação brasileira, política pública, direito constitucional e processo legislativo em todas as esferas (municipal, estadual e federal).

Sua tarefa é analisar a **ementa de uma proposição legislativa** com o objetivo de gerar uma representação estruturada e neutra, no formato JSON, contendo as seguintes dimensões:

1. **Resumo da Proposição (summary)**
   Elabore um resumo objetivo e imparcial em até 3 frases, respondendo às seguintes perguntas:
   - Qual é a intenção ou objetivo principal da proposição?
   - Que mudanças ou criações normativas ela propõe (ex: criação de programa, alteração de lei, regulamentação, etc.)?
   - Há indicação de quem será afetado ou beneficiado?

   Evite repetições da própria ementa.
   Reescreva com clareza, evitando juízo de valor ou opinião.

2. **Abrangência Territorial (scope)**
   Classifique a jurisdição da proposta com base em:
   - Termos como “União”, “nacional”, “território brasileiro”, indicam **Nacional**.
   - Menção a um estado específico, assembleia legislativa, ou governador, indica **Estadual**.
   - Termos como “município”, “prefeito”, “câmara municipal”, indicam **Municipal**.

3. **Magnitude do Impacto (magnitude)**
   Avalie o grau e o alcance do impacto conforme os critérios abaixo:
   - **Baixo**: afeta apenas uma entidade específica, ou introduz pequenas mudanças.
   - **Médio**: mudanças pontuais que afetam parte de uma política pública ou setor.
   - **Alto**: mudanças estruturais, institucionais ou orçamentárias relevantes.
   - **Setorial Específico**: afeta um setor econômico, categoria profissional ou política pública específica (ex: saúde, educação, transporte).
   - **População Geral**: impacto generalizado na sociedade (ex: sistema tributário, previdência, eleições, criminalização de condutas).

4. **Tags Temáticas (tags)**
   Extraia de 3 a 5 palavras-chave temáticas que representem a proposição.
   Ex: ["educação", "escolas públicas", "financiamento", "crianças"]

   Dica: Foque nos assuntos centrais da proposição, evitando termos vagos como "lei", "política", "medida", etc.

5. **Estimativa de Impacto por LLM (llm_impact_estimate)**
   Atribua um valor subjetivo de 0 a 30 representando a relevância política e social da proposta.
   Baseie-se nos seguintes critérios:
   - **Baixa pontuação (0-10)**: proposta local, técnica, com escopo restrito.
   - **Média (11-20)**: impacto relevante em um setor, categoria ou grupo social.
   - **Alta (21-30)**: temas estruturais, sensíveis, com alto potencial de debate público, judicialização ou repercussão política.

   Seja criterioso e imparcial.
   Propostas polêmicas, estruturantes ou amplamente aplicáveis tendem a ter notas maiores.
   ---

Você deve retornar **apenas** um objeto JSON com os campos abaixo, e nada mais:

{
  "proposicao_id": "ID da proposição",
  "summary": "Resumo em 2–3 frases",
  "scope": "Municipal | Estadual | Nacional",
  "magnitude": "Baixo | Médio | Alto | Setorial Específico | População Geral",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "llm_impact_estimate": 0
}`}
            </code>
          </Box>
        </Paper>
      </Paper>
    </Box>
  );
}