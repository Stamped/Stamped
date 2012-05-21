//
//  STSimpleTimes.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleTimes.h"
#import "STSimpleHours.h"

@implementation STSimpleTimes

@synthesize sun = _sun;
@synthesize mon = _mon;
@synthesize tue = _tue;
@synthesize wed = _wed;
@synthesize thu = _thu;
@synthesize fri = _fri;
@synthesize sat = _sat;

-(id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    _sun = [[decoder decodeObjectForKey:@"sun"] retain];
    _mon = [[decoder decodeObjectForKey:@"mon"] retain];
    _tue = [[decoder decodeObjectForKey:@"tue"] retain];
    _wed = [[decoder decodeObjectForKey:@"wed"] retain];
    _thu = [[decoder decodeObjectForKey:@"thu"] retain];
    _fri = [[decoder decodeObjectForKey:@"fri"] retain];
    _sat = [[decoder decodeObjectForKey:@"sat"] retain];
  }
  return self;
}

- (void)dealloc
{
  [_sun release];
  [_mon release];
  [_tue release];
  [_wed release];
  [_thu release];
  [_fri release];
  [_sat release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.sun forKey:@"sun"];
  [encoder encodeObject:self.mon forKey:@"mon"];
  [encoder encodeObject:self.tue forKey:@"tue"];
  [encoder encodeObject:self.wed forKey:@"wed"];
  [encoder encodeObject:self.thu forKey:@"thu"];
  [encoder encodeObject:self.fri forKey:@"fri"];
  [encoder encodeObject:self.sat forKey:@"sat"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleTimes class]];
  
  RKObjectMapping* hoursMapping = [STSimpleHours mapping];
  
  NSArray* days = [NSArray arrayWithObjects:@"sun", @"mon", @"tue", @"wed", @"thu", @"fri" @"sat", nil];
  
  for (NSString* day in days) {
    [mapping mapRelationship:day withMapping:hoursMapping];
  }
  
  return mapping;
}

@end
