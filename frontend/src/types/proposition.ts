export interface Proposal {
  id: string;
  title: string;
  status: string;
  author: string;
  createdAt: Date;
  siglaTipo: string;
  numero: number;
  ano: number;
  impact_score: number | null;
}