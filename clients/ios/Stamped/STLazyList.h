//
//  STModelLazyList.h
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STLazyList;

@protocol STLazyListDelegate <NSObject>

@optional
- (void)lazyListDidReload:(id<STLazyList>)lazyList;
- (void)lazyListDidGrow:(id<STLazyList>)lazyList;
- (void)lazyListDidShrink:(id<STLazyList>)lazyList;
- (void)lazyListDidReachMaxCount:(id<STLazyList>)lazyList;
- (void)lazyListDidFail:(id<STLazyList>)lazyList;

@end

@protocol STLazyList <NSObject>

- (void)growToCount:(NSInteger)count;
- (void)shrinkToCount:(NSInteger)count;
- (id)objectAtIndex:(NSInteger)index;
- (void)prepareRange:(NSRange)range;
- (void)reload;
- (void)cancelPendingRequests;

- (void)addDelegate:(id<STLazyListDelegate>)delegate;
- (void)removeDelegate:(id<STLazyListDelegate>)delegate;

@property (nonatomic, readonly, assign) NSInteger count;

@property (nonatomic, readonly, retain) NSError* lastError;

@end
