export type QueryType =
  | 'all'
  | 'book'
  | 'website'
  | 'data'
  | 'code'
  | 'collection'
  | 'research article'

export interface Type {
  title: string
  author: string
  keywords: string[]
}
