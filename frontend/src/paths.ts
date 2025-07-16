// frontend/src/paths.ts

export const paths = {
  home: '/',
  auth: { signIn: '/auth/sign-in', signUp: '/auth/sign-up', resetPassword: '/auth/reset-password' },
  dashboard: {
    overview: '/dashboard',
    account: '/dashboard/account',
    proposals: '/dashboard/proposals',
    proposal: (id: number | string) => `/dashboard/proposals/${id}`,
    deputados: '/dashboard/deputados',
    deputado: (id: number | string) => `/dashboard/deputados/${id}`,
    transparency: '/dashboard/transparency',
    integrations: '/dashboard/integrations',
    settings: '/dashboard/settings',
  },
  errors: { notFound: '/errors/not-found' },
} as const;