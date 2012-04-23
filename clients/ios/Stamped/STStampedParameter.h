//
//  STStampedParameter.h
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STStampedParameter : NSObject

- (NSMutableDictionary*)asDictionaryParams;

- (void)importDictionaryParams:(NSDictionary*)params;

@end
