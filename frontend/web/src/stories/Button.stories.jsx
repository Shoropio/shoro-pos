import React from 'react'
import { Button } from '../components/Button'

export default {
  title: 'UI/Button',
  component: Button,
}

export const Primary = () => <Button>Primary</Button>
export const Ghost = () => <Button className="btn-ghost">Ghost</Button>
