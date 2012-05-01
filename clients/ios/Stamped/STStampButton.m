//
//  STStampButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampButton.h"
#import "Util.h"
#import "STCreateStampViewController.h"

@interface STStampButton ()

@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readwrite, retain) id<STEntity> entity;

- (id)initWithEntity:(id<STEntity>)entity andUser:(id<STUser>)user;

@end

@implementation STStampButton

@synthesize user = _user;
@synthesize entity = _entity;

- (id)initWithEntity:(id<STEntity>)entity andUser:(id<STUser>)user {
  self = [super initWithNormalOffImage:[UIImage imageNamed:@"sDetailBar_btn_restamp"] offText:@"Stamp" andOnText:@"Stamped"];
  if (self) {
    self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_restamp_active"];
    self.touchedOnImage= [UIImage imageNamed:@"sDetailBar_btn_restamp_active"];
    self.normalOffImage = [UIImage imageNamed:@"sDetailBar_btn_restamp"];
    _user = [user retain];
    _entity = [entity retain];
  }
  return self;
}

- (id)initWithStamp:(id<STStamp>)stamp
{
  return [self initWithEntity:stamp.entity andUser:stamp.user];
}

- (id)initWithEntity:(id<STEntity>)entity {
  return [self initWithEntity:entity andUser:nil];
}

- (void)defaultHandler:(id)myself {
  if (self.entity) {
    UINavigationController* controller = [Util sharedNavigationController];
    UIViewController* createStamp = [[[STCreateStampViewController alloc] initWithEntity:self.entity] autorelease];
    [controller pushViewController:createStamp animated:YES];
  }
}

@end
