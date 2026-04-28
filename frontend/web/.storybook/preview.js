export const parameters = {
  actions: { argTypesRegex: '^on.*' },
}

export const decorators = [(Story) => (
  <div style={{ padding: '1rem' }}>
    <Story />
  </div>
)]
