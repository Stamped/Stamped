//
//  STEntitySearch.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySearch.h"
#import "Util.h"

@implementation STEntitySearch

@synthesize query = query_;
@synthesize coordinates = coordinates_;
@synthesize category = category_;
@synthesize subcategory = subcategory_;
@synthesize local = local_;
@synthesize page = page_;

- (void)dealloc
{
  [query_ release];
  [coordinates_ release];
  [category_ release];
  [subcategory_ release];
  [local_ release];
  [page_ release];
  [super dealloc];
}

+ (NSArray*)simpleKeyPaths {
  return [NSArray arrayWithObjects:@"coordinates", @"category", @"subcategory", @"local", @"page", nil];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [Util sparseDictionaryForObject:self andKeyPaths:[STEntitySearch simpleKeyPaths]];
  if (self.query) {
    [dict setObject:self.query forKey:@"query"];
  }
  return dict;
}

- (void)importDictionaryParams:(NSDictionary*)params {
  for (NSString* keyPath in [STEntitySearch simpleKeyPaths]) {
    id value = [params objectForKey:keyPath];
    if (value) {
      [self setValue:value forKeyPath:keyPath];
    }
  }
  if ([params objectForKey:@"query"]) {
    self.query = [params objectForKey:@"query"];
  }
}

@end
