def hensel_lift(curve, P):
  """
  Calculate Lifted Point using Hensel's Lemma
  Args:
    curve: The Elliptic Curve
    P: A point on curve
  Returns:
    The "lifted" Point
  """
  from ecpy.util import modinv
  x, y, _ = map(int, tuple(P))
  p = curve.field.p
  t = (((x * x * x + curve.a * x + curve.b) - y * y) / p) % p
  t = (t * modinv(2 * y, p)) % p
  return (x, y + (curve.field.p * t))


def SSSA_Attack(F, E, P, Q):
  """
  Solve ECDLP using SSSA(Semaev-Smart-Satoh-Araki) Attack.
  Args:
    F: The Base Field
    E: The Elliptic Curve
    P: A point on E
    Q: A point on E
  Returns:
    Return x where satisfies Q = xP.
  """
  from ecpy.structure.EllipticCurve import EllipticCurve
  from ecpy.structure.RationalField import QQ
  from ecpy.structure.Zmod import Zmod
  from ecpy.util import modinv, is_enable_native
  A = E.a
  # lP, lQ, ... is "lifted" P, Q, ...
  x1, y1 = hensel_lift(E, P)
  x2, y2 = hensel_lift(E, Q)
  lF = Zmod(F.p ** 2)
  lA = (y2 * y2 - y1 * y1 - (x2 * x2 * x2 - x1 * x1 * x1))
  lA = (lA * modinv(x2 - x1, lF.n)) % lF.n
  lB = (y1 * y1 - x1 * x1 * x1 - A * x1) % lF.n
  if not is_enable_native:
    lE = EllipticCurve(lF, lA, lB)
    lP = lE(x1, y1)
    lQ = lE(x2, y2)
    lU = (F.p - 1) * lP
    lV = (F.p - 1) * lQ
    dx1 = ((int(lU.x) - int(lP.x)) / F.p) % F.p
    dx2 = int(lU.y) - int(lP.y)
    dy1 = int(lV.x) - int(lQ.x)
    dy2 = (int(lV.y) - int(lQ.y)) % F.p
    m = dy1 * modinv(dx1, F.p) * dx2 * modinv(dy2, F.p)
    return int(QQ(m, F.p) % F.p)
  else:
    from ecpy.native import *
    lE = EC_create(lA, lB, "FF")
    modulo = F.p ** 2
    lP = EP_FF_create(lE, x1, y1, 1, modulo)
    lQ = EP_FF_create(lE, x2, y2, 1, modulo)
    lU = lP * (F.p - 1)
    lV = lQ * (F.p - 1)
    lPx, lPy, lPz = lP.tuple()
    lQx, lQy, lQz = lQ.tuple()
    lUx, lUy, lUz = lU.tuple()
    lVx, lVy, lVz = lV.tuple()
    lUx = (lUx * modinv(lUz, modulo)) % modulo
    lUy = (lUy * modinv(lUz, modulo)) % modulo
    lVx = (lVx * modinv(lVz, modulo)) % modulo
    lVy = (lVy * modinv(lVz, modulo)) % modulo
    dx1 = ((lUx - lPx) / F.p) % F.p
    dx2 = lUy - lPy
    dy1 = lVx - lQx
    dy2 = (lVy - lQy) % F.p
    m = dy1 * modinv(dx1, F.p) * dx2 * modinv(dy2, F.p)
    return int(QQ(m, F.p) % F.p)
