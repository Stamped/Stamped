//
//  STRdio.m
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRdio.h"
#import <Rdio/Rdio.h>
#import "Util.h"
#import "STConfirmationView.h"
#import "STPlaylistPopUp.h"
#import "STSimpleAction.h"
#import "STRdioPlaylistPopUp.h"
#import "STPlayer.h"
#import "STPlayerPopUp.h"
#import "STSimplePlaylistItem.h"
#import "STSimpleAction.h"
#import "STConfiguration.h"

static NSString* _rdioTokenKey = @"STRdio.token";

@interface STRdioPlaylistHelper : NSObject <RDAPIRequestDelegate>

- (id)initWithID:(NSString*)rdioID;
+ (void)dispatchWithID:(NSString*)rdioID;

@property (nonatomic, readonly, copy) NSString* rdioId;

@end

@interface STRdioPlayerHelper : NSObject <RDAPIRequestDelegate>

- (id)initWithID:(NSString*)rdioID;
+ (void)dispatchWithID:(NSString*)rdioID;

@property (nonatomic, readonly, copy) NSString* rdioId;

@end

@interface STRdio () <RdioDelegate>

- (BOOL)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag;
- (void)addToPlaylist:(NSString*)rdioID;

@property (nonatomic, readwrite, assign) BOOL loggedIn;
@property (nonatomic, readwrite, copy) NSString* accessToken;
@property (nonatomic, readwrite, copy) STCallback callback;
@property (nonatomic, readwrite, assign) BOOL waitingForResponse;

@end

@implementation STRdio

@synthesize rdio = _rdio;
@synthesize loggedIn = _loggedIn;
@synthesize accessToken = _accessToken;
@synthesize callback = _callback;
@synthesize waitingForResponse = _waitingForResponse;

static STRdio* _sharedInstance;

- (id)init {
    self = [super init];
    if (self) {
        _rdio = [[Rdio alloc] initWithConsumerKey:@"bzj2pmrs283kepwbgu58aw47"
                                        andSecret:@"xJSZwBZxFp" delegate:self];
    }
    return self;
}

- (void)dealloc
{
    [_accessToken release];
    [_rdio release];
    [_callback release];
    [super dealloc];
}

+ (void)initialize {
    _sharedInstance = [[STRdio alloc] init];
}

+ (STRdio*)sharedRdio {
    return _sharedInstance;
}

- (void)logout {
    [self.rdio logout];
    self.loggedIn = NO;
    self.accessToken = nil;
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:_rdioTokenKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
}

- (BOOL)connected {
    NSString* token = [[NSUserDefaults standardUserDefaults] stringForKey:_rdioTokenKey];
    return token != nil;
}

- (void)ensureLoginWithCompletionBlock:(void(^)(void))block {
    self.callback = block;
    UIWindow* window = [[UIApplication sharedApplication] keyWindow];
    NSString* token = [[NSUserDefaults standardUserDefaults] stringForKey:_rdioTokenKey];
    if (token) {
        [self.rdio authorizeUsingAccessToken:token fromController:window.rootViewController];
    }
    else {
        [self.rdio authorizeFromController:window.rootViewController];
    }
}

- (void)startPlayback:(NSString*)rdioID {
    if (self.loggedIn) {
        [self.rdio.player playSource:rdioID];
    }
    else {
        [self ensureLoginWithCompletionBlock:^{
            if(self.loggedIn) {
                [self startPlayback:rdioID];
            }
        }];
    }
}

- (void)stopPlayback {
    if (self.loggedIn) {
        [self.rdio.player stop];
    }
    else {
        NSLog(@"tried to stop Rdio without being signed in");
    }
}

- (void)addToPlaylist:(NSString*)rdioID {
    if (self.loggedIn) {
        [STRdioPlaylistHelper dispatchWithID:rdioID];
    }
    else {
        [self ensureLoginWithCompletionBlock:^{
            if(self.loggedIn) {
                [self addToPlaylist:rdioID];
            }
        }];
    }
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    return [self didChooseSource:source forAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    [self didChooseSource:source forAction:action withContext:context shouldExecute:YES];
}

- (NSString*)itemIDForItem:(id<STPlaylistItem>)item {
    if (item.action.sources.count) {
        for (id<STSource> source in item.action.sources) {
            if ([source.source isEqual:@"rdio"]) {
                return source.sourceID;
            }
        }
    }
    return nil;
}

- (NSArray<STPlaylistItem>*)itemsForSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    NSArray<STImage>* images = nil;
    if (context.entityDetail.images.count) {
        id<STImageList> first = [context.entityDetail.images objectAtIndex:0];
        images = first.sizes;
    }
    NSString* defaultSubtitle = nil;
    NSString* subcategory = context.entityDetail.subcategory;
    if ([subcategory isEqualToString:@"artist"]) {
        defaultSubtitle = [NSString stringWithFormat:@"By %@", context.entityDetail.title];
    }
    else if ([subcategory isEqualToString:@"album"]) {
        defaultSubtitle = [NSString stringWithFormat:@"From %@", context.entityDetail.title];
    }
    else if ([subcategory isEqualToString:@"song"]) {
        defaultSubtitle = context.entityDetail.caption;
    }
    if (context.entityDetail.playlist.data.count > 0 && source.sourceID) {
        NSMutableArray<STPlaylistItem>* array = [NSMutableArray array];
        for (NSInteger i = 0; i < context.entityDetail.playlist.data.count; i++) {
            id<STPlaylistItem> item = [context.entityDetail.playlist.data objectAtIndex:i];
            NSString* itemID = [self itemIDForItem:item];
            if (itemID) {
                STSimplePlaylistItem* simpleItem = [[STSimplePlaylistItem playlistItemWithItem:item] retain];
                [array addObject:simpleItem];
                if (!simpleItem.images) {
                    simpleItem.images = images;
                }
                if (!simpleItem.subtitle) {
                    simpleItem.subtitle = defaultSubtitle;
                }
            }
        }
        return array;
    }
    else {
        STSimplePlaylistItem* item = [[[STSimplePlaylistItem alloc] init] autorelease];
        item.name = context.entityDetail.title;
        item.action = [STSimpleAction actionWithType:action andSource:source];
        if (!item.images) {
            item.images = images;
        }
        if (!item.subtitle) {
            item.subtitle = defaultSubtitle;
        }
        [item retain];
        return [NSArray arrayWithObject:item];
    }
}

- (BOOL)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
    BOOL handled = NO;
    if ([source.source isEqualToString:@"rdio"]) {
//        if ([action isEqualToString:@"listen"] && source.sourceID != nil ) {
//            handled = TRUE;
//            if (flag) {
//                //NSLog(@"playing song:%@",context.entityDetail);
//                [self ensureLoginWithCompletionBlock:^{
//                    if (self.loggedIn) {
//                        BOOL revert = [STConfiguration flag:STPlayerRevertKey];
//                        if (revert) {
//                            //[STPlayer sharedInstance] addPlaylistItem:<#(id<STPlaylistItem>)#> atIndex:<#(NSInteger)#>
//                            [Util setFullScreenPopUp:[[[STRdioPlaylistPopUp alloc] initWithSource:source action:action andContext:context] autorelease] 
//                                         dismissible:NO 
//                                      withBackground:[UIColor colorWithWhite:0 alpha:.3]];
//                            
//                        }
//                        else {
//                            NSArray<STPlaylistItem>* items = [self itemsForSource:source forAction:action withContext:context];
//                            [STPlayerPopUp presentWithItems:items clear:![STConfiguration flag:STPlayerCummulativeKey]];
//                            
//                        }
//                    }
//                }];
//                //[self startPlayback:source.sourceID];
//            }
//        }
        if ([action isEqualToString:@"playlist"] && source.sourceID != nil) {
            handled = TRUE;
            if (flag) {
                [self addToPlaylist:source.sourceID];
            }
        }
    }
    return handled;
}

- (void) rdioDidAuthorizeUser:(NSDictionary *)user withAccessToken:(NSString *)accessToken {
    self.loggedIn = YES;
    self.accessToken = accessToken;
    [[NSUserDefaults standardUserDefaults] setValue:accessToken forKey:_rdioTokenKey];
    [[NSUserDefaults standardUserDefaults] synchronize];
    //NSLog(@"Storing:%@",accessToken);
    if (self.callback) {
        self.callback();
    }
    self.callback = nil;
}

- (void) rdioAuthorizationFailed:(NSString *)error {
    self.loggedIn = NO;
    self.accessToken = nil;
    if (self.callback) {
        self.callback();
    }
    self.callback = nil;
}

- (void) rdioAuthorizationCancelled {
    self.loggedIn = NO;
    self.accessToken = nil;
    if (self.callback) {
        self.callback();
    }
    self.callback = nil;
}

- (void) rdioDidLogout {
    self.loggedIn = NO;
    self.accessToken = nil;
    if (self.callback) {
        self.callback();
    }
    self.callback = nil;
}

@end

@implementation STRdioPlaylistHelper

@synthesize rdioId = _rdioId;

+ (void)dispatchWithID:(NSString*)rdioID {
    // TODO MEMORY_LEAK
    STRdioPlaylistHelper* helper = [[STRdioPlaylistHelper alloc] initWithID:rdioID];
    NSMutableDictionary *params = [NSMutableDictionary dictionary];
    NSString* userKey = [[STRdio sharedRdio].rdio.user objectForKey:@"key"];
    [params setObject:userKey forKey:@"user"];
    [[STRdio sharedRdio].rdio callAPIMethod:@"getPlaylists" withParameters:params delegate:helper];
}

- (id)initWithID:(NSString *)rdioID {
    self = [super init];
    if (self) {
        _rdioId = [rdioID copy];
    }
    return self;
}

- (void)dealloc
{
    [_rdioId release];
    [super dealloc];
}

#pragma mark RDAPIRequestDelegate
/**
 * Our API call has returned successfully.
 * the data parameter can be an NSDictionary, NSArray, or NSData 
 * depending on the call we made.
 *
 * Here we will inspect the parameters property of the returned RDAPIRequest
 * to see what method has returned.
 */
- (void)rdioRequest:(RDAPIRequest *)request didLoadData:(id)data {
    NSString* playlistName = @"From Stamped";
    NSString *method = [request.parameters objectForKey:@"method"];
    //NSLog(@"method:%@:%@",method,data);
    if( [method isEqualToString:@"getPlaylists"] ) {
        //TODO reconsider type checking approach for potentially corrupt data
        NSString* stampedPlaylistID = nil;
        if ([data respondsToSelector:@selector(objectForKey:)]) {
            id owned = [data objectForKey:@"owned"];
            if (owned != nil && [owned isKindOfClass:[NSArray class]]) {
                NSArray* ownedArray = (NSArray*) owned;
                for (NSInteger i=0; i < ownedArray.count; i++) {
                    id playlist = [ownedArray objectAtIndex:i];
                    if (playlist != nil && [playlist respondsToSelector:@selector(objectForKey:)]) {
                        id name = [playlist objectForKey:@"name"];
                        if (name != nil && [name isEqualToString:playlistName]) {
                            stampedPlaylistID = [playlist objectForKey:@"key"];
                            if (stampedPlaylistID != nil) {
                                break;
                            }
                        }
                    }
                }
            }
        }
        if (stampedPlaylistID == nil) {
            NSMutableDictionary* params = [NSMutableDictionary dictionary];
            [params setObject:playlistName forKey:@"name"];
            [params setObject:@"Songs added by Stamped" forKey:@"description"];
            [params setObject:self.rdioId forKey:@"tracks"];
            [[STRdio sharedRdio].rdio callAPIMethod:@"createPlaylist" withParameters:params delegate:self];
        }
        else {
            NSMutableDictionary* params = [NSMutableDictionary dictionary];
            [params setObject:stampedPlaylistID forKey:@"playlist"];
            [params setObject:self.rdioId forKey:@"tracks"];
            [[STRdio sharedRdio].rdio callAPIMethod:@"addToPlaylist" withParameters:params delegate:self];
        }
    }
    if ( [method isEqualToString:@"createPlaylist"] || [method isEqualToString:@"addToPlaylist"]) {
        [self autorelease];
        [STConfirmationView displayConfirmationWithTitle:@"Added to Rdio" subtitle:@"Playlist 'From Stamped'" andIconImage:[UIImage imageNamed:@"3rd_icon_rdio"]];
    }
}

- (void)rdioRequest:(RDAPIRequest *)request didFailWithError:(NSError*)error {
    //log and ignore for now
    //TODO
    NSLog(@"Rdio addToPlaylist failed:%@",error);
    [self autorelease];
}

@end
