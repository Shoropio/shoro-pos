export const Input = (props) => {
  const { value, onChange, ...rest } = props
  return <input className="input" value={value} onChange={onChange} {...rest} />
}
