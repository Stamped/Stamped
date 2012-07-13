//
//  STTodosPageSource.m
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTodosPageSource.h"
#import "STStampedAPI.h"

@interface STTodosPageSource ()
@end

@implementation STTodosPageSource

- (id)initWithCoder:(NSCoder *)decoder {
    return [self init];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    //Nothing
}

- (STCancellation*)pageStartingAtDate:(NSDate*)date
                      withMinimumSize:(NSInteger)minimumSize
                        preferredSize:(NSInteger)preferredSize 
                          andCallback:(void (^)(STCachePage* page, NSError* error, STCancellation* cancellation))block {
    return [[STStampedAPI sharedInstance] todosWithDate:date
                                                  limit:minimumSize
                                                 offset:0
                                            andCallback:^(NSArray<STTodo> *todos, NSError *error, STCancellation *cancellation) {
                                                if (todos) {
                                                    STCachePage* page = [[[STCachePage alloc] initWithObjects:todos 
                                                                                                        start:date
                                                                                                          end:nil
                                                                                                      created:nil 
                                                                                                      andNext:nil] autorelease];
                                                    block(page, nil, cancellation);
                                                }
                                                else {
                                                    block(nil, error, cancellation);
                                                }
                                            }];
}

@end
