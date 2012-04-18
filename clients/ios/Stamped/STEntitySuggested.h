//
//  STEntitySuggested.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STEntitySuggested : NSObject

@property (nonatomic, readwrite, copy) NSString* coordinates;
@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSString* subcategory;
@property (nonatomic, readwrite, copy) NSNumber* limit;

- (NSMutableDictionary*)asDictionaryParams;

- (void)importDictionaryParams:(NSDictionary*)params;

@end
