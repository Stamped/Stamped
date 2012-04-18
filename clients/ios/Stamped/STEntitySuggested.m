//
//  STEntitySuggested.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySuggested.h"
#import "Util.h"

@implementation STEntitySuggested

@synthesize coordinates = coordinates_;
@synthesize category = category_;
@synthesize subcategory = subcategory_;
@synthesize limit = limit_;

+ (NSArray*)allKeys {
  return [NSArray arrayWithObjects:@"coordinates", @"category", @"subcategory", @"limit", nil];
}

- (void)dealloc
{
  [coordinates_ release];
  [category_ release];
  [subcategory_ release];
  [limit_ release];
  [super dealloc];
}

- (NSMutableDictionary *)asDictionaryParams {
  NSMutableDictionary* dictionary = [Util sparseDictionaryForObject:self 
                                                        andKeyPaths:[STEntitySuggested allKeys]];
  return dictionary;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  for (NSString* keyPath in [STEntitySuggested allKeys]) {
    if ([params objectForKey:keyPath]) {
      [self setValue:[params objectForKey:keyPath] forKeyPath:keyPath];
    }
  }
}


@end
