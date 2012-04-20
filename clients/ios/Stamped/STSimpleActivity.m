//
//  STSimpleActivity.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivity.h"
#import "STSimpleUser.h"
#import "STSimpleActivityObjects.h"
#import "STSimpleActivityReference.h"
#import "STSimpleAction.h"

@implementation STSimpleActivity

@synthesize header = header_;
@synthesize body = body_;
@synthesize footer = footer_;

@synthesize benefit = benefit_;
@synthesize created = created_;
@synthesize icon = icon_;
@synthesize image = image_;

@synthesize subjects = subjects_;
@synthesize verb = verb_;
@synthesize objects = objects_;
@synthesize action = action_;

@synthesize headerReferences = headerReferences_;
@synthesize bodyReferences = bodyReferences_;
@synthesize footerReferences = footerReferences_;

- (void)dealloc
{
  [header_ release];
  [body_ release];
  [footer_ release];
  
  [benefit_ release];
  [created_ release];
  [icon_ release];
  [image_ release];
  
  [subjects_ release];
  [verb_ release];
  [objects_ release];
  [action_ release];
  
  [headerReferences_ release];
  [bodyReferences_ release];
  [footerReferences_ release];
  
  [super dealloc];
}

+ (RKObjectMapping *)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivity class]];
  
  [mapping mapAttributes:
   @"header",
   @"body",
   @"footer",
   @"benefit",
   @"created",
   @"icon",
   @"image",
   @"verb",
   nil];
  
  [mapping mapRelationship:@"subjects" withMapping:[STSimpleUser mapping]];
  [mapping mapRelationship:@"objects" withMapping:[STSimpleActivityObjects mapping]];
  [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
  
  [mapping mapKeyPath:@"header_references" toRelationship:@"headerReferences" withMapping:[STSimpleActivityReference mapping]];
  [mapping mapKeyPath:@"body_references" toRelationship:@"bodyReferences" withMapping:[STSimpleActivityReference mapping]];
  [mapping mapKeyPath:@"footer_references" toRelationship:@"footerReferences" withMapping:[STSimpleActivityReference mapping]];
  return mapping;
}

@end
