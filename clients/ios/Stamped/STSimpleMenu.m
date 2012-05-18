//
//  STSimpleMenu.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleMenu.h"
#import "STSimpleSubmenu.h"

@implementation STSimpleMenu

@synthesize disclaimer = _disclaimer;
@synthesize attributionImage = _attributionImage;
@synthesize attributionImageLink = _attributionImageLink;
@synthesize menus = _menus;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _disclaimer = [[decoder decodeObjectForKey:@"disclaimer"] retain];
    _attributionImage = [[decoder decodeObjectForKey:@"attributiionImage"] retain];
    _attributionImageLink = [[decoder decodeObjectForKey:@"attributionImageLink"] retain];
    _menus = [[decoder decodeObjectForKey:@"menus"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_disclaimer release];
  [_attributionImage release];
  [_attributionImageLink release];
  [_menus release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.disclaimer forKey:@"disclaimer"];
  [encoder encodeObject:self.attributionImage forKey:@"attributionImage"];
  [encoder encodeObject:self.attributionImageLink forKey:@"attributionImageLink"];
  [encoder encodeObject:self.menus forKey:@"menus"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleMenu class]];
  
  [mapping mapKeyPathsToAttributes:
   @"attribution_image", @"attributionImage",
   @"attribution_image_link", @"attributionImageLink",
   nil];
  
  [mapping mapAttributes:
   @"disclaimer",
   nil];
  
  [mapping mapRelationship:@"menus" withMapping:[STSimpleSubmenu mapping]];
  
  return mapping;
}

@end
