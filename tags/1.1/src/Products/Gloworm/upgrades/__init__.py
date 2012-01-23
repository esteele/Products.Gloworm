from Products.CMFCore.utils import getToolByName

def null_upgrade_step(context):
    pass

def upgrade1to2(context):
    context = getToolByName(context, "portal_setup")
    context.runAllImportStepsFromProfile('profile-Products.Gloworm.upgrades:1to2', purge_old=False)
