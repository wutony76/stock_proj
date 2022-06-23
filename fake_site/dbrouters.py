ALIAS_BY_LABEL = {
  "fatcat": "fatcat",
  "scratch": "scratch",
}

class DBRouter(object):

  def db_for_read(self, model, **hints):
    return ALIAS_BY_LABEL.get(model._meta.app_label, None)

  def db_for_write(self, model, **hints):
    return ALIAS_BY_LABEL.get(model._meta.app_label, None)

