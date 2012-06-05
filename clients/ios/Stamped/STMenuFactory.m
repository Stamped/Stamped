//
//  STMenuFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMenuFactory.h"
#import "Util.h"
#import "STSimpleMenu.h"
#import <RestKit/RestKit.h>
#import "STRestKitLoader.h"

static NSString* const kMenuLookupPath = @"/entities/menu.json";

@implementation STMenuFactory

static STMenuFactory* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STMenuFactory alloc] init];
}

- (void)menuWithEntityId:(NSString*)anEntityID andCallbackBlock:(void (^)(id<STMenu>))aBlock {
  NSDictionary* params = [NSDictionary dictionaryWithObject:anEntityID forKey: @"entity_id"];
  [[STRestKitLoader sharedInstance] loadWithPath:kMenuLookupPath 
                                            post:NO
                                   authenticated:YES
                                          params:params 
                                         mapping:[STSimpleMenu mapping] 
                                     andCallback:^(NSArray* array, NSError* error, STCancellation* cancellation) {
    id<STMenu> menu = nil;
    if (array && [array count] > 0) {
      menu = [array objectAtIndex:0];
    }
    aBlock(menu);
  }];
}

+ (STMenuFactory*)sharedFactory {
  return _sharedInstance;
}

@end
