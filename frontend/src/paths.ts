// frontend/src/paths.ts

export const paths = {
  home: '/',
  auth: { signIn: '/auth/sign-in', signUp: '/auth/sign-up', resetPassword: '/auth/reset-password' },
  dashboard: {
    overview: '/dashboard',
    account: '/dashboard/account',
    proposals: '/dashboard/proposals',
    deputados: '/dashboard/deputados',
    deputado: (id: number | string) => `/dashboard/deputados/${id}`, // Add this line for dynamic paths
    transparency: '/dashboard/transparency',
    integrations: '/dashboard/integrations',
    settings: '/dashboard/settings',
  },
  errors: { notFound: '/errors/not-found' },
} as const;