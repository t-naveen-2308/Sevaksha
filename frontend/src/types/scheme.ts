export interface Scheme {
  scheme_id: string;
  scheme_name: string;
  min_age?: number;
  max_age?: number;
  income_limit?: number;
  target_occupation?: string;
  eligibility_criteria?: string;
  required_documents?: string;
  scheme_description?: string;
  application_process?: string;
  benefits?: string;
  application_link?: string;
}
