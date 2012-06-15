//
//  STStampNew.m
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampNew.h"

@implementation STStampNew

@synthesize entityID = _entityID;
@synthesize searchID = _searchID;
@synthesize blurb = _blurb;
@synthesize credit = _credit;

- (void)dealloc
{
  [_entityID release];
  [_searchID release];
  [_blurb release];
  [_credit release];
  [super dealloc];
}

+ (NSArray*)keyPaths {
  return [NSArray arrayWithObjects:@"entityID", @"searchID", @"blurb", @"credit", nil];
}

+ (NSArray*)sourcePaths {
  return [NSArray arrayWithObjects:@"entity_id", @"search_id", @"blurb", @"credits", nil];
}


- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  NSArray* paths = [STStampNew keyPaths];
  NSArray* values = [STStampNew sourcePaths];
  for (NSInteger i = 0; i < paths.count; i++) {
    id value = [self valueForKeyPath:[paths objectAtIndex:i]];
    if (value) {
      [dict setObject:value forKey:[values objectAtIndex:i]];
    }
  }
  return dict;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  [super importDictionaryParams:params];
  NSArray* paths = [STStampNew keyPaths];
  NSArray* values = [STStampNew sourcePaths];
  for (NSInteger i = 0; i < paths.count; i++) {
    id value = [params objectForKey:[values objectAtIndex:i]];
    if (value) {
      [self setValue:value forKey:[paths objectAtIndex:i]];
    }
  }
}

- (void)addCreditWithScreenName:(NSString*)screenName {
    if (screenName == nil) {
        return;
    }
    NSString* cur = self.credit;
    if (!cur && [cur isEqualToString:@""]) {
        self.credit = screenName;
    }
    else {
        self.credit = [NSString stringWithFormat:@"%@,%@", cur, screenName];
    }
}

@end
