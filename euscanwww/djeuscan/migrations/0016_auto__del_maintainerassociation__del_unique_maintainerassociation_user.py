# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'CategoryAssociation', fields ['user', 'category']
        db.delete_unique('djeuscan_categoryassociation', ['user_id', 'category'])

        # Removing unique constraint on 'OverlayAssociation', fields ['user', 'overlay']
        db.delete_unique('djeuscan_overlayassociation', ['user_id', 'overlay'])

        # Removing unique constraint on 'HerdAssociation', fields ['user', 'herd']
        db.delete_unique('djeuscan_herdassociation', ['user_id', 'herd_id'])

        # Removing unique constraint on 'PackageAssociation', fields ['user', 'package']
        db.delete_unique('djeuscan_packageassociation', ['user_id', 'package_id'])

        # Removing unique constraint on 'MaintainerAssociation', fields ['user', 'maintainer']
        db.delete_unique('djeuscan_maintainerassociation', ['user_id', 'maintainer_id'])

        # Deleting model 'MaintainerAssociation'
        db.delete_table('djeuscan_maintainerassociation')

        # Deleting model 'PackageAssociation'
        db.delete_table('djeuscan_packageassociation')

        # Deleting model 'HerdAssociation'
        db.delete_table('djeuscan_herdassociation')

        # Deleting model 'OverlayAssociation'
        db.delete_table('djeuscan_overlayassociation')

        # Deleting model 'CategoryAssociation'
        db.delete_table('djeuscan_categoryassociation')

        # Adding model 'UserProfile'
        db.create_table('djeuscan_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('djeuscan', ['UserProfile'])

        # Adding M2M table for field herds on 'UserProfile'
        db.create_table('djeuscan_userprofile_herds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['djeuscan.userprofile'], null=False)),
            ('herd', models.ForeignKey(orm['djeuscan.herd'], null=False))
        ))
        db.create_unique('djeuscan_userprofile_herds', ['userprofile_id', 'herd_id'])

        # Adding M2M table for field maintainers on 'UserProfile'
        db.create_table('djeuscan_userprofile_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['djeuscan.userprofile'], null=False)),
            ('maintainer', models.ForeignKey(orm['djeuscan.maintainer'], null=False))
        ))
        db.create_unique('djeuscan_userprofile_maintainers', ['userprofile_id', 'maintainer_id'])

        # Adding M2M table for field packages on 'UserProfile'
        db.create_table('djeuscan_userprofile_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['djeuscan.userprofile'], null=False)),
            ('package', models.ForeignKey(orm['djeuscan.package'], null=False))
        ))
        db.create_unique('djeuscan_userprofile_packages', ['userprofile_id', 'package_id'])

        # Adding M2M table for field categories on 'UserProfile'
        db.create_table('djeuscan_userprofile_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['djeuscan.userprofile'], null=False)),
            ('category', models.ForeignKey(orm['djeuscan.category'], null=False))
        ))
        db.create_unique('djeuscan_userprofile_categories', ['userprofile_id', 'category_id'])

        # Adding M2M table for field overlays on 'UserProfile'
        db.create_table('djeuscan_userprofile_overlays', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['djeuscan.userprofile'], null=False)),
            ('overlay', models.ForeignKey(orm['djeuscan.overlay'], null=False))
        ))
        db.create_unique('djeuscan_userprofile_overlays', ['userprofile_id', 'overlay_id'])

        # Adding model 'Category'
        db.create_table('djeuscan_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('djeuscan', ['Category'])

        # Adding model 'Overlay'
        db.create_table('djeuscan_overlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('djeuscan', ['Overlay'])

    def backwards(self, orm):
        # Adding model 'MaintainerAssociation'
        db.create_table('djeuscan_maintainerassociation', (
            ('maintainer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Maintainer'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('djeuscan', ['MaintainerAssociation'])

        # Adding unique constraint on 'MaintainerAssociation', fields ['user', 'maintainer']
        db.create_unique('djeuscan_maintainerassociation', ['user_id', 'maintainer_id'])

        # Adding model 'PackageAssociation'
        db.create_table('djeuscan_packageassociation', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Package'])),
        ))
        db.send_create_signal('djeuscan', ['PackageAssociation'])

        # Adding unique constraint on 'PackageAssociation', fields ['user', 'package']
        db.create_unique('djeuscan_packageassociation', ['user_id', 'package_id'])

        # Adding model 'HerdAssociation'
        db.create_table('djeuscan_herdassociation', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('herd', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Herd'])),
        ))
        db.send_create_signal('djeuscan', ['HerdAssociation'])

        # Adding unique constraint on 'HerdAssociation', fields ['user', 'herd']
        db.create_unique('djeuscan_herdassociation', ['user_id', 'herd_id'])

        # Adding model 'OverlayAssociation'
        db.create_table('djeuscan_overlayassociation', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('overlay', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('djeuscan', ['OverlayAssociation'])

        # Adding unique constraint on 'OverlayAssociation', fields ['user', 'overlay']
        db.create_unique('djeuscan_overlayassociation', ['user_id', 'overlay'])

        # Adding model 'CategoryAssociation'
        db.create_table('djeuscan_categoryassociation', (
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('djeuscan', ['CategoryAssociation'])

        # Adding unique constraint on 'CategoryAssociation', fields ['user', 'category']
        db.create_unique('djeuscan_categoryassociation', ['user_id', 'category'])

        # Deleting model 'UserProfile'
        db.delete_table('djeuscan_userprofile')

        # Removing M2M table for field herds on 'UserProfile'
        db.delete_table('djeuscan_userprofile_herds')

        # Removing M2M table for field maintainers on 'UserProfile'
        db.delete_table('djeuscan_userprofile_maintainers')

        # Removing M2M table for field packages on 'UserProfile'
        db.delete_table('djeuscan_userprofile_packages')

        # Removing M2M table for field categories on 'UserProfile'
        db.delete_table('djeuscan_userprofile_categories')

        # Removing M2M table for field overlays on 'UserProfile'
        db.delete_table('djeuscan_userprofile_overlays')

        # Deleting model 'Category'
        db.delete_table('djeuscan_category')

        # Deleting model 'Overlay'
        db.delete_table('djeuscan_overlay')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djeuscan.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.categorylog': {
            'Meta': {'object_name': 'CategoryLog', '_ormbases': ['djeuscan.Log']},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.euscanresult': {
            'Meta': {'object_name': 'EuscanResult'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'ebuild': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scan_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'djeuscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False'})
        },
        'djeuscan.herdlog': {
            'Meta': {'object_name': 'HerdLog', '_ormbases': ['djeuscan.Log']},
            'herd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Herd']"}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.log': {
            'Meta': {'object_name': 'Log'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n_packages_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_outdated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_upstream': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'djeuscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.maintainerlog': {
            'Meta': {'object_name': 'MaintainerLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Maintainer']"})
        },
        'djeuscan.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_version_gentoo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_gentoo'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'last_version_overlay': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_overlay'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'last_version_upstream': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_upstream'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.problemreport': {
            'Meta': {'object_name': 'ProblemReport'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Version']", 'null': 'True', 'blank': 'True'})
        },
        'djeuscan.refreshpackagequery': {
            'Meta': {'object_name': 'RefreshPackageQuery'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'djeuscan.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Category']", 'symmetrical': 'False'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Herd']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False'}),
            'overlays': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Overlay']", 'symmetrical': 'False'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Package']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'djeuscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'confidence': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ebuild_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'db_index': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vtype': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'djeuscan.versionlog': {
            'Meta': {'object_name': 'VersionLog'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vtype': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'djeuscan.worldlog': {
            'Meta': {'object_name': 'WorldLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['djeuscan']